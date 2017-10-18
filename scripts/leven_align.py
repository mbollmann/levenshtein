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
        plain_aligner = LevenshteinAligner()
        style = self.args.style

        for line in self.args.infile:
            try:
                (word1, word2) = line.strip().decode(self.args.encoding).split('\t')
            except ValueError:
                print >> sys.stderr, "*** Ignoring line: %s" % line

            if self.args.nonid and word1 == word2:
                continue
            if self.args.unusual:
                if word1 == word2:
                    continue
                _, rulesets_w = aligner.perform_levenshtein(word1, word2)
                _, rulesets_p = plain_aligner.perform_levenshtein(word1, word2)
                if set(rulesets_w).issubset(set(rulesets_p)):
                    continue

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
    parser.add_argument('-u', '--unusual',
                        dest="unusual",
                        action='store_true',
                        default=False,
                        help='Only print alignments that would not be possible with plain Levenshtein alignment')

    args = parser.parse_args()

    # launching application ...
    MainApplication(args).run()
