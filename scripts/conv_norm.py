#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
from mblevenshtein import PMILevenshtein

BEGIN_TOKEN = "__BEGIN__"
Begin_TOKEN = "__begin__"
KEEP_LABEL = "__KEEP__"
EPSILON_LABEL = "__EPS__"

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

def process_alignment(alignment, epsilon, keep=False, interspersed=False):
    if interspersed:
        for r in process_alignment_interspersed(alignment, epsilon):
            yield r
        return

    def make(i, o):
        return (i, o if not keep or i != o else KEEP_LABEL)

    input_token = BEGIN_TOKEN
    output_token = epsilon
    for (lhs, rhs) in alignment:
        if lhs == epsilon:
            if output_token == epsilon:
                output_token = rhs
            else:
                output_token += rhs
        else:
            yield make(input_token, output_token)
            input_token = lhs
            output_token = rhs
    yield make(input_token, output_token)

def process_alignment_interspersed(alignment, epsilon):
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
            yield (lhs, rhs)
            input_token, output_token = epsilon, epsilon
    yield (input_token, output_token)

def revert_conversion(data, epsilon):
    def make_output(l, r):
        if r == epsilon:
            return ""
        elif r == KEEP_LABEL:
            return l
        else:
            return r

    input_token, output_token = None, None
    for (lhs, rhs) in data:
        if lhs.lower() == Begin_TOKEN:
            if input_token:
                yield (input_token, output_token)
            input_token = ""
            output_token = make_output(lhs, rhs)
        else:
            if lhs != epsilon:
                input_token += lhs
            output_token += make_output(lhs, rhs)
    if input_token:
        yield (input_token, output_token)

def train_and_align(data, eps, log_to, args):
    use_keep, interspersed = args.use_keep, args.interspersed

    # Train PMI
    pmi = PMILevenshtein()
    pmi.epsilon = eps
    for (source, target) in data:
        pmi.add_pair(source, target)
    if args.param:
        pmi.weights.loadParamFromXMLFile(args.param)
        pmi_align = pmi.perform_alignments()
    else:
        pmi.train(log_to=log_to)
        pmi_align = pmi.alignments

    # Output alignments
    for source_target_pair in data:
        alignments = pmi_align[source_target_pair]
        yield(list(process_alignment(alignments[0], eps,
                                     keep=use_keep,
                                     interspersed=interspersed)))

def main(args, output_to=sys.stdout, log_to=sys.stderr):
    data = process_input(args.infile, args.encoding)
    eps = args.epsilon

    # Revert the conversion?
    if args.revert:
        for tokens in revert_conversion(data, eps):
            output_to.write('\t'.join(tokens).encode("utf-8"))
            output_to.write('\n')
    else:
        for word_pair in train_and_align(data, eps, log_to, args):
            for char_alignment in word_pair:
                output_to.write('\t'.join(char_alignment).encode("utf-8"))
                output_to.write('\n')
            output_to.write('\n')  # empty line between words

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
    parser.add_argument('-f', '--file',
                        dest="param",
                        type=str,
                        help='XML file with Levenshtein weights')
    parser.add_argument('-r', '--revert',
                        action='store_true',
                        default=False,
                        help=('Reverts the conversion, i.e., converts character-level '
                              'representations back to word-level'))
    parser.add_argument('--interspersed',
                        action='store_true',
                        default=False,
                        help=('Intersperse the input word with epsilon characters'))
    parser.add_argument('--use-keep',
                        action='store_true',
                        default=False,
                        help=('Labels identity substitutions with a special ' +
                              KEEP_LABEL + ' symbol'))
    parser.add_argument('--epsilon',
                        type=str,
                        default=EPSILON_LABEL,
                        help='Epsilon symbol to use (default: "%(default)s")')
    parser.add_argument('-e', '--encoding',
                        default='utf-8',
                        help='Encoding of the input file (default: %(default)s)')

    main(parser.parse_args())
