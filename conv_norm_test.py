#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import conv_norm

KEEP_LABEL = conv_norm.KEEP_LABEL
EPS_LABEL = "<<!EPS!>>"

class TestProcessAlignment(unittest.TestCase):
    def test_identity(self):
        a = [('f', 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL))
        expected = [('__BEGIN__', EPS_LABEL)] + a
        self.assertEqual(actual, expected)

    def test_identity_with_keep(self):
        a = [('f', 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, keep=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', KEEP_LABEL), ('o', KEEP_LABEL), ('o', KEEP_LABEL)]
        self.assertEqual(actual, expected)

    def test_deletion(self):
        a = [('f', 'f'), ('o', EPS_LABEL), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL))
        expected = [('__BEGIN__', EPS_LABEL)] + a
        self.assertEqual(actual, expected)

    def test_deletion_with_keep(self):
        a = [('f', 'f'), ('o', EPS_LABEL), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, keep=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', KEEP_LABEL), ('o', EPS_LABEL), ('o', KEEP_LABEL)]
        self.assertEqual(actual, expected)

    def test_insertion(self):
        a = [('f', 'f'), (EPS_LABEL, 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'fo'), ('o', 'o')]
        self.assertEqual(actual, expected)

    def test_insertion_with_keep(self):
        a = [('f', 'f'), (EPS_LABEL, 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, keep=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'fo'), ('o', KEEP_LABEL)]
        self.assertEqual(actual, expected)

    def test_insertion_at_beginning(self):
        a = [(EPS_LABEL, 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL))
        expected = [('__BEGIN__', 'f'), ('o', 'o'), ('o', 'o')]
        self.assertEqual(actual, expected)

    def test_insertion_at_beginning_with_keep(self):
        a = [(EPS_LABEL, 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, keep=True))
        expected = [('__BEGIN__', 'f'), ('o', KEEP_LABEL), ('o', KEEP_LABEL)]
        self.assertEqual(actual, expected)

    def test_mixed_insertion_and_deletion(self):
        a = [('f', 'o'), ('o', EPS_LABEL), (EPS_LABEL, 'x'), ('y', 'n')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'o'), ('o', 'x'), ('y', 'n')]
        self.assertEqual(actual, expected)

    def test_mixed_insertion_and_deletion_with_keep(self):
        a = [('f', 'o'), ('o', EPS_LABEL), (EPS_LABEL, 'x'), ('y', 'n')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, keep=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'o'), ('o', 'x'), ('y', 'n')]
        self.assertEqual(actual, expected)

    def test_interspersed(self):
        a = [('f', 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, interspersed=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'f'),
                    (EPS_LABEL, EPS_LABEL), ('o', 'o'),
                    (EPS_LABEL, EPS_LABEL), ('o', 'o'), (EPS_LABEL, EPS_LABEL)]
        self.assertEqual(actual, expected)

    def test_deletion_interspersed(self):
        a = [('f', 'f'), ('o', EPS_LABEL), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, interspersed=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'f'),
                    (EPS_LABEL, EPS_LABEL), ('o', EPS_LABEL),
                    (EPS_LABEL, EPS_LABEL), ('o', 'o'), (EPS_LABEL, EPS_LABEL)]
        self.assertEqual(actual, expected)

    def test_insertion_interspersed(self):
        a = [('f', 'f'), (EPS_LABEL, 'o'), ('o', 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, interspersed=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'f'),
                    (EPS_LABEL, 'o'), ('o', 'o'), (EPS_LABEL, EPS_LABEL)]
        self.assertEqual(actual, expected)

    def test_insertion_at_the_end_interspersed(self):
        a = [('f', 'f'), ('o', 'o'), (EPS_LABEL, 'o')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, interspersed=True))
        expected = [('__BEGIN__', EPS_LABEL), ('f', 'f'),
                    (EPS_LABEL, EPS_LABEL), ('o', 'o'), (EPS_LABEL, 'o')]
        self.assertEqual(actual, expected)

    def test_multi_insertion(self):
        a = [('a', 'f'), (EPS_LABEL, 'r'), (EPS_LABEL, 'u'), ('b', 'b')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL))
        expected = [('__BEGIN__', EPS_LABEL), ('a', 'fru'), ('b', 'b')]
        self.assertEqual(actual, expected)

    def test_multi_insertion_interspersed(self):
        a = [('a', 'f'), (EPS_LABEL, 'r'), (EPS_LABEL, 'u'), ('b', 'b')]
        actual = list(conv_norm.process_alignment(a, EPS_LABEL, interspersed=True))
        expected = [('__BEGIN__', EPS_LABEL), ('a', 'f'),
                    (EPS_LABEL, 'ru'), ('b', 'b'), (EPS_LABEL, EPS_LABEL)]
        self.assertEqual(actual, expected)


class TestRevertConversion(unittest.TestCase):
    def test_identity(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foo', 'foo')]
        self.assertEqual(actual, expected)

    def test_identity_with_keep(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', KEEP_LABEL), ('o', KEEP_LABEL), ('o', KEEP_LABEL)]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foo', 'foo')]
        self.assertEqual(actual, expected)

    def test_deletion(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'f'), ('o', EPS_LABEL), ('o', 'o')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foo', 'fo')]
        self.assertEqual(actual, expected)

    def test_deletion_with_keep(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', KEEP_LABEL), ('o', EPS_LABEL), ('o', KEEP_LABEL)]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foo', 'fo')]
        self.assertEqual(actual, expected)

    def test_insertion(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'fo'), ('o', 'o')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('fo', 'foo')]
        self.assertEqual(actual, expected)

    def test_insertion_with_keep(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'fo'), ('o', KEEP_LABEL)]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('fo', 'foo')]
        self.assertEqual(actual, expected)

    def test_insertion_at_beginning(self):
        a = [('__BEGIN__', 'f'), ('o', 'o'), ('o', 'o')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('oo', 'foo')]
        self.assertEqual(actual, expected)

    def test_insertion_at_beginning_with_keep(self):
        a = [('__BEGIN__', 'f'), ('o', KEEP_LABEL), ('o', KEEP_LABEL)]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('oo', 'foo')]
        self.assertEqual(actual, expected)

    def test_mixed_insertion_and_deletion(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'o'), ('o', 'x'), ('y', 'n')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foy', 'oxn')]
        self.assertEqual(actual, expected)

    def test_mixed_insertion_and_deletion_with_keep(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'o'), ('o', 'x'), ('y', 'n')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foy', 'oxn')]
        self.assertEqual(actual, expected)

    def test_interspersed(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'f'),
             (EPS_LABEL, EPS_LABEL), ('o', 'o'),
             (EPS_LABEL, EPS_LABEL), ('o', 'o')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foo', 'foo')]
        self.assertEqual(actual, expected)

    def test_deletion_interspersed(self):
        a = [('__BEGIN__', EPS_LABEL), ('f', 'f'),
             (EPS_LABEL, EPS_LABEL), ('o', EPS_LABEL),
             (EPS_LABEL, EPS_LABEL), ('o', 'o')]
        actual = list(conv_norm.revert_conversion(a, EPS_LABEL))
        expected = [('foo', 'fo')]
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
