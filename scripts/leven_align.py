#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
from mblevenshtein import LevenshteinAligner, LevenshteinWeights

class MainApplication(object):
    args = None
    weights = None

    def __init__(self, args):
        self.args = args
        if args.param:
            self.weights = LevenshteinWeights(args.param, args.type)
        else:
            self.weights = LevenshteinWeights()

    def run(self):
        aligner = LevenshteinAligner(weights=self.weights)
        style = self.args.style
        nonid = self.args.nonid

        for line in self.args.infile:
            try:
                (word1, word2) = line.strip().decode(self.args.encoding).split('\t')
            except ValueError:
                print >> sys.stderr, "*** Ignoring line: %s" % line

            if not (nonid and word1 == word2):
                aligner.print_alignments(word1, word2, style)

if __name__ == '__main__':
    description = "Takes an XML file containing Levenshtein weights and prints character alignments for given word pairs."
    epilog = ""
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='File containing word pairs to align, tab-separated (default: <STDIN>)')
    parser.add_argument('-e', '--encoding',
                        default='utf-8',
                        help='Encoding of the input file (default: utf-8)')
    parser.add_argument('-f', '--file',
                        dest="param",
                        type=str,
                        help='Parameter file')
    parser.add_argument('-t', '--type',
                        choices=['tabbed','xml'],
                        default='xml',
                        help='Parameter file format (default: %(default)s)')
    parser.add_argument('-s', '--style',
                        choices=['linear','verbose'],
                        default='verbose',
                        help='Output style (default: %(default)s)')
    parser.add_argument('-n', '--non-identical',
                        dest="nonid",
                        action='store_true',
                        default=False,
                        help='Only print alignments for non-identical word pairs')

    args = parser.parse_args()

    # launching application ...
    MainApplication(args).run()
