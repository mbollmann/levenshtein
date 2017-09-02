#!/usr/bin/env python3

import argparse

from mblearn.data import TextData
from mblevenshtein import LevenshteinWeights
import edlib
import sys

WORD_SEP = '÷'

def read_data(source):
    data = TextData()
    data.read_vertical(source)
    return data

class AsciiMapper:
    def __init__(self, alphabet):
        self.codes = set(range(128))
        self.map_to_ascii = {}
        self.map_to_char  = {}
        # first, remove all actually used codes
        for char in alphabet:
            if ord(char) < 128:
                self.codes.remove(ord(char))
        # then, map multibyte-chars to free codes
        for char in alphabet:
            if ord(char) >= 128:
                code = self.codes.pop()
                self.map_to_ascii[char] = chr(code)
                self.map_to_char[chr(code)] = char

    def encode(self, string):
        for orig, replacement in self.map_to_ascii.items():
            string = string.replace(orig, replacement)
        return string

    def decode(self, string):
        for orig, replacement in self.map_to_char.items():
            string = string.replace(orig, replacement)
        return string


def unroll_cigar(a, b, cigar):
    i, j = 0, 0
    s, t = [], []
    def flush(word_a, word_b):
        print("{}\t{}".format(''.join(word_a), ''.join(word_b)))

    operations, num = [], None
    for char in cigar:
        if char in "0123456789":
            num = char if num is None else num + char
        else:
            operations.append((int(num), char))
            num = None

    for count, op in operations:
        count = int(count)
        if op == 'D':
            t += b[j:j+count]
            j += count
        elif op == 'I':
            for char in a[i:i+count]:
                if char == WORD_SEP:
                    flush(s, t)
                    s, t = [], []
                else:
                    s.append(char)
            i += count
        else:
            for ca, cb in zip(a[i:i+count], b[j:j+count]):
                if ca == WORD_SEP:
                    flush(s, t)
                    s, t = [], []
                    if cb != WORD_SEP:
                        t.append(cb)
                else:
                    s.append(ca)
                    t.append(cb)
            i += count
            j += count

    if s or t:
        flush(s, t)


def main(args):
    file_a, file_b = read_data(args.file_a.read()), read_data(args.file_b.read())
    print("Sentences in file A: {}".format(file_a.sentence_count), file=sys.stderr)
    print("Sentences in file B: {}".format(file_b.sentence_count), file=sys.stderr)

    alphabet = set(file_a.characters) | set(file_b.characters)
    alphabet.add(WORD_SEP)
    mapper = AsciiMapper(alphabet)

    edlib_opts = {
        'task': 'path'
    }
    if args.weights:
        weights = LevenshteinWeights(filename=args.weights)
        additionalEqualities = []
        for ((a, b), cost) in weights.weights.items():
            if cost < args.weight_limit:
                additionalEqualities.append((
                    mapper.encode(a), mapper.encode(b)
                    ))
        edlib_opts['additionalEqualities'] = additionalEqualities

    for (sent_a, sent_b) in zip(file_a.sentences, file_b.sentences):
        a, b = WORD_SEP.join(sent_a), WORD_SEP.join(sent_b)
        aligned = edlib.align(mapper.encode(a), mapper.encode(b), **edlib_opts)
        #print(aligned)
        unroll_cigar(a, b, aligned['cigar'])
        print()


if __name__ == '__main__':
    description = "Word-aligns sentences from two text files (in vertical format)."
    epilog = ("This scripts uses 'edlib' instead of my own Levenshtein functions "
              "for performance reasons.  This means it can't use weights for the "
              "comparison; instead, some characters can be defined as equal "
              "depending on a given weight distribution (options -w/-l).")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('file_a',
                        metavar='INPUT1',
                        type=argparse.FileType('r', encoding="utf-8"),
                        help='First input file')
    parser.add_argument('file_b',
                        metavar='INPUT2',
                        type=argparse.FileType('r', encoding="utf-8"),
                        help='Second input file')
    parser.add_argument('-w', '--weights',
                        metavar='XMLFILE',
                        type=str,
                        help=('XML file with Levenshtein weights; can be used '
                              'to treat character pairs with very low weight '
                              'as equal for the comparison'))
    parser.add_argument('-l', '--weight-limit',
                        default=0.2,
                        type=float,
                        help=('Maximum weight when supplying -w/--weights '
                              '(default: %(default)f)'))

    args = parser.parse_args()
    main(args)
