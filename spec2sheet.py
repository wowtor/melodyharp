#!/usr/bin/env python3

import argparse
import csv
import math

import confidence
import svgwrite


class Note:
    def __init__(self, line, length):
        self.line = line
        self.length = length

    def position(self, x, y):
        self.x = x
        self.y = y

    def symbol(self):
        loglen = -round(math.log2(self.length))
        symbols = [ '\U0001D15D', '\U0001D15E', '\U0001D15F', '\U0001D160', '\U0001D161', ]

        if math.isclose(2**-loglen, self.length):
            return symbols[loglen]
        elif math.isclose(2**-loglen/2 * 1.5, self.length):
            return symbols[loglen+1] + '.'
        else:
            return '?'


def draw_sheet(dwg, title, scale, notes, line_offsets):
    if title is not None:
        g = dwg.g(style='font-size:30pt; text-align: center; width: 100%')
        g.add(dwg.text(title, insert=('80mm', '50mm')))
        dwg.add(g)

    total_duration = 0 if len(notes) <= 1 else sum([note.length for note in notes]) - notes[-1].length
    total_width = 297

    cursor = 0
    for note in notes:
        x = cursor * total_width / total_duration
        x -= 297/2
        x *= scale
        x += 297/2
        note.position(x, line_offsets[note.line])
        cursor += note.length

    g_notes = dwg.g(style='font-size:30pt')
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
            notes.append(Note(int(row[0])-1, float(row[1])))

    return title, scale, notes


def get_output_path(path):
    if path.endswith('.csv'):
        return path[:-4] + '.svg'


def main():
    parser = argparse.ArgumentParser(description='Melodieharp bladmuziek.')
    parser.add_argument('--output', '-o', metavar='FILE', help='Write SVG output to FILE')
    parser.add_argument('csv', metavar='FILE', help='Read from FILE', nargs=1)

    args = parser.parse_args()

    line_offsets = [ 210 - 25 - i*12.5 for i in range(15) ]
    dwg = draw_template(args.output or get_output_path(args.csv[0]), line_offsets)

    title, scale, notes = load_csv(args.csv[0])

    draw_sheet(dwg, title, scale, notes, line_offsets)
    
    dwg.save()


if __name__ == '__main__':
    main()
