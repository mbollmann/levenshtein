#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import argparse
from mblevenshtein import PMILevenshtein
from operator import itemgetter

class MainApplication(object):
    args = None
    pmi  = None
    divisor = 10

    def __init__(self, args):
        self.args = args
        self.pmi = PMILevenshtein()
        self.pmi.learning_rate = args.lr
        self.divisor = args.divisor

    def read_input_data(self):
        enc = self.args.encoding
        for line in self.args.infile:
            line = line.strip().decode(enc)
            if not line.count('\t')==1:
                continue
            (source, target) = line.split('\t')
            source = source.strip()
            target = target.strip()
            self.pmi.add_pair(source, target)

    def run(self):
        self.read_input_data()
        self.pmi.train()

        if args.generate == "weights":
            self.pmi.weights.reset_weights()
            minval = 0.1
            for (rule, weight) in self.pmi.find_ngram_weights(n=self.args.ngram).iteritems():
                (source, target) = rule
                if source == '<eps>': continue
                if weight > (len(source) * self.divisor): continue
                self.pmi.weights.set_weight(source, target, max((weight * 1.0 / self.divisor), minval))

        if self.args.savefile:
            self.args.savefile.write(self.pmi.weights.make_xml_param())


        def utfprint(string):
            print string.encode("utf-8").replace('<eps>','')
        for (rule, dist) in sorted(self.pmi.weights.weights.items(), key=itemgetter(1)):
            if rule[0] != rule[1] :
                utfprint("%s\t%s\t%f" % (rule[0], rule[1], dist))


if __name__ == '__main__':
    description = "Calculates Levenshtein weights based on training pairs of source--target wordforms."
    epilog = ""
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='Training data to process, tab-separated (default: <STDIN>)')
    parser.add_argument('-e', '--encoding',
                        default='utf-8',
                        help='Encoding of the input file (default: %(default)s)')
    parser.add_argument('-f', '--file',
                        dest="savefile",
                        type=argparse.FileType('w'),
                        help='Save parameter file as XML')
    parser.add_argument('-g', '--generate',
                        choices=('pmi', 'weights'),
                        default='weights',
                        help=('Choose whether to output weights for '
                              'Levenshtein normalization (after Adesam '
                              'et al., 2012) or only the weights '
                              'generated during the PMI alignment; '
                              'if the latter, options -n/-d have no '
                              'effect (default: %(default)s)'))
    parser.add_argument('-l', '--lr',
                        metavar="LR",
                        type=float,
                        default=0.2,
                        help='Learning rate for weight adjustments (default: %(default)f)')
    parser.add_argument('-n', '--ngram',
                        metavar="N",
                        type=int,
                        default=3,
                        help='Collect n-grams of up to length N (default: %(default)i)')
    parser.add_argument('-d', '--divisor',
                        metavar="N",
                        type=float,
                        default=7,
                        help='Divide final weights by this factor (default: %(default)i)')

    args = parser.parse_args()

    # launching application ...
    MainApplication(args).run()
