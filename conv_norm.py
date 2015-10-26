#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
from Levenshtein import LevenshteinAligner
from PMILevenshtein import PMILevenshtein

BEGIN_TOKEN = "__BEGIN__"

def process_input(data, enc):
    processed = []
    for line in data:
        line = line.strip().decode(enc)
        if not line:
            continue
        if line.count("\t") != 1:
            print >> sys.stderr, "*** Ignoring line: {0}".format(line.encode("utf-8"))
            continue
        (source, target) = line.split("\t")
        source = source.strip()
        target = target.strip()
        processed.append((source, target))
    return processed

def process_alignment(alignment, epsilon):
    input_token = BEGIN_TOKEN
    output_token = epsilon
    for (lhs, rhs) in alignment:
        if lhs == epsilon:
            if output_token == epsilon:
                output_token = rhs
            else:
                output_token += rhs
        else:
            yield (input_token, output_token)
            input_token = lhs
            output_token = rhs
    yield (input_token, output_token)

def revert_conversion(data, epsilon):
    input_token, output_token = None, None
    for (lhs, rhs) in data:
        if lhs == BEGIN_TOKEN:
            if input_token:
                yield (input_token, output_token)
            input_token = ""
            output_token = rhs if rhs != epsilon else ""
        else:
            input_token += lhs
            if rhs != epsilon:
                output_token += rhs
    if input_token:
        yield (input_token, output_token)

def main(args):
    data = process_input(args.infile, args.encoding)
    eps = args.epsilon

    # Revert the conversion?
    if args.revert:
        for tokens in revert_conversion(data, eps):
            print('\t'.join(tokens).encode("utf-8"))
        exit(0)

    # Train PMI
    pmi = PMILevenshtein()
    for (source, target) in data:
        pmi.add_pair(source, target)
    pmi.train()

    # Align and output
    aligner = LevenshteinAligner(weights=pmi.weights)
    aligner.epsilon = eps
    for (source, target) in data:
        (_, alignments) = aligner.perform_levenshtein(source, target)
        # output character-level normalization from first alignment:
        for tokens in process_alignment(alignments[0], eps):
            print('\t'.join(tokens).encode("utf-8"))
        print("")

if __name__ == '__main__':
    description = ("Converts word-level normalizations to character-level "
                   "normalizations (or vice versa), using PMI Levenshtein "
                   "alignment.")
    epilog = ("Calling this script on a given INFILE is equivalent to "
              "calling train_pmi.py on INFILE to generate Levenshtein weights, "
              "then calling leven_align.py on INFILE with the generated "
              "weights, and finally applying a rightward merging of insertions "
              "on the best alignment to arrive at the character-level "
              "normalizations.")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='Word-level normalizations, tab-separated (default: <STDIN>)')
    parser.add_argument('-r', '--revert',
                        action='store_true',
                        default=False,
                        help=('Reverts the conversion, i.e., converts character-level '
                              'representations back to word-level'))
    parser.add_argument('--epsilon',
                        type=str,
                        default="<eps>",
                        help='Epsilon symbol to use (default: "%(default)s")')
    parser.add_argument('-e', '--encoding',
                        default='utf-8',
                        help='Encoding of the input file (default: %(default)s)')

    main(parser.parse_args())
