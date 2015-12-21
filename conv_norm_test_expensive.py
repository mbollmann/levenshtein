#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from hypothesis import given, Settings
import hypothesis.strategies as st

from StringIO import StringIO
import unicodedata
import sys
import conv_norm

def valid_category(cat):
    return (not cat.startswith("C") and not cat.startswith("Z"))

ALPHABET = [c for c in map(unichr, range(0x110000)) \
            if valid_category(unicodedata.category(c))]
TOKEN = st.text(alphabet=ALPHABET, min_size=1, max_size=15, average_size=6)
DOCUMENT = st.lists(elements=st.tuples(TOKEN, TOKEN), min_size=1, max_size=100)

def convert_to_stringio(data):
    sio = StringIO()
    for (source, target) in data:
        sio.write(source.strip().encode("utf-8"))
        sio.write('\t')
        sio.write(target.strip().encode("utf-8"))
        sio.write('\n')
    sio.seek(0)
    return sio

class MockArgs(object):
    infile = None
    revert = False
    epsilon = "<eps>"
    encoding = "utf-8"
    use_keep = False
    interspersed = False

    def __init__(self, infile=None):
        self.infile = infile

def perform_convert_revert(args, sio):
    # convert
    converted = StringIO()
    conv_norm.main(args, output_to=converted, log_to=None)
    # revert
    converted.seek(0)
    reverted = StringIO()
    args.infile = converted
    args.revert = True
    conv_norm.main(args, output_to=reverted, log_to=None)
    # check
    sio.seek(0)
    reverted.seek(0)
    original = sio.readlines()
    generated = reverted.readlines()
    return (original, generated)

class TestReversion(unittest.TestCase):
    @given(tokens=DOCUMENT, settings=Settings(max_examples=50))
    def test_reverting_conversion(self, tokens):
        sys.stderr.write("#")
        sio = convert_to_stringio(tokens)
        args = MockArgs(infile=sio)
        (original, generated) = perform_convert_revert(args, sio)
        self.assertTrue(len(original) > 0)
        self.assertTrue(len(generated) > 0)
        self.assertEqual(original, generated)

    @given(tokens=DOCUMENT, settings=Settings(max_examples=50))
    def test_reverting_conversion_with_keep(self, tokens):
        sys.stderr.write("#")
        sio = convert_to_stringio(tokens)
        args = MockArgs(infile=sio)
        args.use_keep = True
        (original, generated) = perform_convert_revert(args, sio)
        self.assertTrue(len(original) > 0)
        self.assertTrue(len(generated) > 0)
        self.assertEqual(original, generated)

if __name__ == '__main__':
    unittest.main()
