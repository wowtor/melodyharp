#!/usr/bin/env python3

import unittest

import spec2sheet


class Test(unittest.TestCase):
    def test_get_note(self):
        for octaaf in [0, 1, -1, 2, -2]:
            basis = octaaf*12
            c = spec2sheet.Note(basis, 1, False, 'c')
            self.assertEqual(spec2sheet.get_note(c, 'g').tone, basis-5)
            self.assertEqual(spec2sheet.get_note(c, 'a').tone, basis-3)
            self.assertEqual(spec2sheet.get_note(c, 'b').tone, basis-1)
            self.assertEqual(spec2sheet.get_note(c, 'c').tone, basis)
            self.assertEqual(spec2sheet.get_note(c, 'd').tone, basis+2)
            self.assertEqual(spec2sheet.get_note(c, 'e').tone, basis+4)
            self.assertEqual(spec2sheet.get_note(c, 'f').tone, basis+5)

        for octaaf in [0, 1, -1, 2, -2]:
            basis = octaaf*12+1 # cis
            cis = spec2sheet.Note(basis, 1, False, 'c')
            self.assertEqual(spec2sheet.get_note(cis, 'g').tone, basis-6)
            self.assertEqual(spec2sheet.get_note(cis, 'a').tone, basis-4)
            self.assertEqual(spec2sheet.get_note(cis, 'b').tone, basis-2)
            self.assertEqual(spec2sheet.get_note(cis, 'c').tone, basis-1)
            self.assertEqual(spec2sheet.get_note(cis, 'd').tone, basis+1)
            self.assertEqual(spec2sheet.get_note(cis, 'e').tone, basis+3)
            self.assertEqual(spec2sheet.get_note(cis, 'f').tone, basis+4)

        for octaaf in [0, 1, -1, 2, -2]:
            basis = octaaf*12-1 # b
            b = spec2sheet.Note(basis, 1, False, 'b')
            self.assertEqual(spec2sheet.get_note(b, 'f').tone, basis-6)
            self.assertEqual(spec2sheet.get_note(b, 'g').tone, basis-4)
            self.assertEqual(spec2sheet.get_note(b, 'a').tone, basis-2)
            self.assertEqual(spec2sheet.get_note(b, 'b').tone, basis)
            self.assertEqual(spec2sheet.get_note(b, 'c').tone, basis+1)
            self.assertEqual(spec2sheet.get_note(b, 'd').tone, basis+3)
            self.assertEqual(spec2sheet.get_note(b, 'e').tone, basis+5)


if __name__ == '__main__':
    unittest.main()
