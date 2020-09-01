#!/usr/bin/env python3

import argparse
import collections
import csv
import math
import os
import re

import svgwrite


class NoteSymbol:
    def __init__(self, line, length, silent=False):
        self.line = line
        self.length = length
        self.silent = silent

    def position(self, x, y):
        self.x = x
        self.y = y

    def symbol(self):
        loglen = -round(math.log2(self.length))
        voice_symbols = [ '\U0001D15D', '\U0001D15E', '\U0001D15F', '\U0001D160', '\U0001D161', ]
        rest_symbols = [ '\U0001D13B', '\U0001D13C', '\U0001D13D', '\U0001D13E', '\U0001D13F', ]

        symbols = voice_symbols if not self.silent else rest_symbols

        if math.isclose(2**-loglen, self.length):
            return symbols[loglen]
        elif math.isclose(2**-loglen/2 * 1.5, self.length):
            return symbols[loglen+1] + '.'
        else:
            return '?'


def draw_sheet(dwg, title, scale, notes, line_offsets, shift=0):
    if title is not None:
        g = dwg.g(style='font-size: 20pt; text-align: center; width: 100%')
        g.add(dwg.text(title, insert=('80mm', '50mm')))
        dwg.add(g)

    total_duration = 0 if len(notes) <= 1 else sum([note.length for note in notes]) - notes[-1].length
    total_width = 297

    cursor = 0
    for note in notes:
        if note.line >= len(line_offsets):
            raise ValueError(f'line {note.line} is out of range (instrument has {len(line_offsets)} lines)')

        x = (cursor / total_duration + shift) * total_width
        x -= 297/2
        x *= scale
        x += 297/2
        note.position(x, line_offsets[note.line])
        cursor += note.length

    g_notes = dwg.g(style='font-size:20pt')
    previous_note = None
    for i, note in enumerate(notes):
        g_notes.add(dwg.text(note.symbol(), insert=(f'{note.x}mm', f'{note.y}mm')))
        if previous_note is not None and previous_note.y != note.y:
            g_notes.add(dwg.line((f'{note.x}mm', f'{note.y}mm'), (f'{previous_note.x}mm', f'{previous_note.y}mm'), stroke='black', stroke_dasharray='2,5'))
        previous_note = note
    dwg.add(g_notes)


def draw_template(path, line_offsets):
    dwg = svgwrite.Drawing(filename=path, size=('297mm', '210mm'))

    # draw cut lines
    dwg.add(dwg.line(('95mm',  '0mm'), ('0cm',   '193mm'), stroke=svgwrite.rgb(10, 10, 16, '%')))
    dwg.add(dwg.line(('202mm', '0mm'), ('297mm', '193mm'), stroke=svgwrite.rgb(10, 10, 16, '%')))

    # draw note lines
    for offset in line_offsets:
        dwg.add(dwg.line(('0mm', f'{offset}mm'), ('297mm', f'{offset}mm'), stroke=svgwrite.rgb(90, 90, 90, '%')))

    return dwg


def load_csv(path):
    title = None
    scale = 1
    notes = []

    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == 'Title':
                title = row[1]
            elif row[0] == 'Scale':
                scale = float(row[1])
            elif row[0] == 'Notes':
                break
        for row in reader:
            base = 0
            tonemap = [ 0, 2, 4, 6, 7, 9, 11 ]

            line = int(row[0])
            tone = tonemap[line % 7] + (line//7)*12 + base
            real_duration = float(row[1])
            duration = 2 ** math.ceil(math.log2(1/real_duration))
            dot = 1/duration < real_duration
            base_name = None
            note = Note(tone, duration, dot, base_name)
            notes.append(note)

    return title, scale, notes


class VersionState:
    def __init__(self, parser):
        self._parser = parser

    def __call__(self, token):
        if token == '"2.18.2"':
            self._parser._state = ClosedState(self._parser)
        else:
            raise ValueError(f'unrecognized version: {token}')


TONEMAP = {
    'a': -3,
    'ais': -2,
    'bes': -2,
    'b': -1,
    'c': 0,
    'cis': 1,
    'des': 1,
    'd': 2,
    'dis': 3,
    'ees': 3,
    'e': 4,
    'f': 5,
    'fis': 6,
    'ges': 6,
    'g': 7,
    'gis': 8,
    'aes': 8,
}


"""
tone: int: relative tone
duration: int: 1 / (tone duration without augmentation)
dot: boolean: indicates extended duration
base_name: str: name without augmentations (a..g)
"""
Note = collections.namedtuple('Note', ['tone', 'duration', 'dot', 'name'])


class RelativeState:
    def __init__(self, parser):
        self._parser = parser

    def __call__(self, token):
        self._parser.updateRelative(token)
        self._parser._state = ClosedState(self._parser)


class IgnoreState:
    def __init__(self, parser, ntokens):
        self._parser = parser
        self._remaining = ntokens

    def __call__(self, token):
        self._remaining -= 1
        if self._remaining == 0:
            self._parser._state = ClosedState(self._parser)


class ClosedState:
    def __init__(self, parser):
        self._parser = parser

    def __call__(self, token):
        if token == r'\version':
            self._parser._state = VersionState(self._parser)
        elif token == r'\relative':
            self._parser._state = RelativeState(self._parser)
        elif token == r'\time':
            self._parser._state = IgnoreState(self._parser, 1)
        elif token == r'\clef':
            self._parser._state = IgnoreState(self._parser, 1)
        elif token == r'\key':
            self._parser._state = IgnoreState(self._parser, 2)
        elif token == r'\bar':
            self._parser._state = IgnoreState(self._parser, 1)
        elif token in ['{', '}']:
            pass
        elif '|' in token:
            pass
        else:
            self._parser.addNote(token)


class LilypondParser:
    def __init__(self):
        self._state = ClosedState(self)
        self._relative = None
        self.notes = []

    def process(self, tokens):
        for token in tokens:
            self._state(token)

        self.compress()
        return self.notes

    def getPreviousDuration(self):
        if len(self.notes) > 1:
            return self.notes[-1].duration
        else:
            return 4

    def getPreviousTone(self):
        for note in reversed(self.notes):
            if note.tone is not None:
                return note.tone, note.name

        if self._relative is not None:
            return self._relative.tone, self._relative.name
        else:
            return 0, 'c'

    def getNote(self, token):
        tone = None
        duration = self.getPreviousDuration()
        dot = False

        m = re.match("^([abcdefgr])(is|e?s)?([',]*)([12468]*)([.]?)$", token)

        if not m:
            raise ValueError(f'invalid token: {token}')

        noot = m.group(1)
        base_name = noot
        if noot == 'r':
            tone = None
        else:
            if m.group(2):
                if m.group(2) in ['s', 'es']:
                    noot += 'es'
                else:
                    noot += 'is'

            relative_tone, relative_name = self.getPreviousTone()
            pitchup = (ord(base_name) - ord(relative_name)) % 7 <= 3
            relative_octave = 12 * (relative_tone // 12)
            if pitchup:
                tone = relative_octave + TONEMAP[noot] - 12
                while tone < relative_tone and relative_tone - tone > 5:
                    tone += 12
            else:
                tone = relative_octave + TONEMAP[noot] + 12
                while tone > relative_tone and tone - relative_tone > 5:
                    tone -= 12

            for char in m.group(3):
                if char == ',':
                    tone -= 12
                else:
                    tone += 12

        if m.group(4):
            duration = int(m.group(4))

        if m.group(5):
            dot = True

        return Note(tone, duration, dot, base_name)

    def compress(self):
        first_index = next(i for i, note in enumerate(self.notes) if note.tone is not None)
        last_index = next(i for i in range(len(self.notes)-1, 0, -1) if self.notes[i].tone is not None)
        self.notes = self.notes[first_index:last_index+1]

    def addNote(self, token):
        self.notes.append(self.getNote(token))

    def updateRelative(self, token):
        self._relative = self.getNote(token)


def get_lowest_tone(notes):
    return min(note.tone if note.tone is not None else 2**32 for note in notes)


def adjust_clef(instrument_clef, notes):
    lowest_tone = get_lowest_tone(notes)
    while instrument_clef > lowest_tone:
        instrument_clef -= 12
    while instrument_clef <= lowest_tone - 12:
        instrument_clef += 12

    return instrument_clef


def get_note_symbol(note, clef, previous):
    CLEF = [0, None, 1, None, 2, 3, None, 4, None, 5, None, 6]
    tone = note.tone
    if tone is None:
        tone = previous
    if tone is None:
        tone = clef

    if CLEF[(tone - clef) % 12] is None:
        raise ValueError(f'tone {(tone - clef) % 12} not supported by instrument')

    line = CLEF[(tone - clef) % 12] + 7 * ((tone-clef)//12)
    silent = note.name == 'r'
    return NoteSymbol(line, 1/note.duration * (1.5 if note.dot else 1), silent=silent)


def load_lilypond(path):
    title = None
    scale = 1
    notes = []

    with open(path, 'r') as f:
        lines = f.readlines()
        lines = [re.sub('%.*', '', line) for line in lines]
        tokens = [token.strip() for token in ' '.join(lines).split() if token.strip() != '']
        notes = list(LilypondParser().process(tokens))

    return title, scale, notes


def get_output_path(path):
    filename, ext = os.path.splitext(path)
    if ext in ['.csv', '.ly']:
        return f'{filename}.svg'
    else:
        return f'{path}.svg'


def get_instrument_clef(value):
    value = value.lower()
    clefs = {
        'c': 0,
        'd': 2,
        'e': 4,
        'f': 5,
        'g': 7,
        'a': 8,
        'b': 10,
    }

    if value not in clefs:
        raise ValueError(f'unrecognized instrument clef: {value}')

    return clefs[value]


def main():
    parser = argparse.ArgumentParser(description='Melodieharp bladmuziek.')
    parser.add_argument('--title', metavar='TITLE', help='Specify a title')
    parser.add_argument('--output', '-o', metavar='FILE', help='Write SVG output to FILE')
    parser.add_argument('--scale', metavar='FACTOR', default=.7, type=float, help='Scale plot to fit sheet')
    parser.add_argument('--shift', metavar='FACTOR', default=0, type=float, help='Shift plot to fit sheet')
    parser.add_argument('--clef', metavar='CLEF', default='g', type=str, help='Instrumet clef (default: g)')
    parser.add_argument('file', metavar='FILE', help='Read from FILE (CSV or Lilypond)', nargs=1)

    args = parser.parse_args()

    sourcefile = args.file[0]

    instrument_clef = get_instrument_clef(args.clef)

    if sourcefile.endswith('.csv'):
        title, scale, notes = load_csv(sourcefile)
    elif sourcefile.endswith('.ly'):
        title, scale, notes = load_lilypond(sourcefile)
    else:
        raise ValueError(f'{sourcefile}: unrecognized file format')

    scale = args.scale
    title = args.title
    instrument_clef = adjust_clef(instrument_clef, notes)

    symbols = []
    previous_tone = None
    for note in notes:
        symbols.append(get_note_symbol(note, instrument_clef, previous_tone))
        if note.tone is not None:
            previous_tone = note.tone

    notes = symbols


    line_offsets = [ 210 - 25 - i*12.5 for i in range(20) ]
    dwg = draw_template(args.output or get_output_path(sourcefile), line_offsets)

    draw_sheet(dwg, title, scale, notes, line_offsets, shift=args.shift)
    
    dwg.save()


if __name__ == '__main__':
    main()
