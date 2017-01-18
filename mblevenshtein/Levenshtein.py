#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, math
from normalizer_exceptions import InitError
from itertools import product
from operator import itemgetter
from WeightedLevenshtein import LevenshteinWeights

class Levenshtein(object):
    # standard Levenshtein has no weights
    def return_weights(self):
        return []

class RuleSet(list):
    def copy_append(self, newitem):
        n = RuleSet(self)
        n.append(newitem)
        return n

class LevenshteinAligner(object):
    weights = None
    epsilon = '<eps>'

    def __init__(self, weights=None, epsilon='<eps>'):
        if weights is None:
            self.weights = LevenshteinWeights()
        else:
            self.weights = weights
        self.epsilon = epsilon

    def perform_levenshtein(self, source, target):
        n, m = len(source), len(target)
        w = self.weights.get_weight
        eps = self.epsilon

        # d keeps numeric distance, e keeps edit operations
        d = [[-1 for y in range(m+1)] for x in range(n+1)]
        e = [[[] for y in range(m+1)] for x in range(n+1)]

        # top row and left column
        d[0][0] = 0.0
        e[0][0] = [RuleSet()]
        for p in range(m):
            editop = (eps, target[p])
            d[0][p+1] = d[0][p] + w(*editop)
            e[0][p+1].append(e[0][p][0].copy_append(editop))
        for p in range(n):
            editop = (source[p], eps)
            d[p+1][0] = d[p][0] + w(*editop)
            e[p+1][0].append(e[p][0][0].copy_append(editop))

        # rest of the matrix
        for i, j in product(range(n),range(m)):
            ins_op = (eps, target[j])
            del_op = (source[i], eps)
            sub_op = (source[i], target[j])
            ins_cost = d[i+1][j] + w(*ins_op)
            del_cost = d[i][j+1] + w(*del_op)
            sub_cost = d[i][j]   + w(*sub_op)

            best_cost   = min(ins_cost, del_cost, sub_cost)
            d[i+1][j+1] = best_cost

            if ins_cost <= best_cost:
                for ruleset in e[i+1][j]:
                    e[i+1][j+1].append(ruleset.copy_append(ins_op))
            if del_cost <= best_cost:
                for ruleset in e[i][j+1]:
                    e[i+1][j+1].append(ruleset.copy_append(del_op))
            if sub_cost <= best_cost:
                for ruleset in e[i][j]:
                    e[i+1][j+1].append(ruleset.copy_append(sub_op))

        # return minimal cost and best alignment(s)
        return (d[n][m], e[n][m])

    def print_alignments(self, source, target, style="verbose"):
        (d, e) = self.perform_levenshtein(source, target)

        def utfprint(string):
            print string.encode("utf-8")

        if style=='verbose':
            utfprint("Pair:  %s -- %s  / Distance: %f" % (source, target, d))
            for ruleset in e:
                print
                utfprint(' '.join(map(itemgetter(0), ruleset)).replace(self.epsilon,' '))
                utfprint(' '.join(map(itemgetter(1), ruleset)).replace(self.epsilon,' '))
            print("--------------------------------------------------------------")
        elif style=='linear':
            ruleset = e[0]   # only take the first ruleset
            rulelist = ['='.join(rule).replace(self.epsilon,'') for rule in ruleset]
            utfprint('|' + '|'.join(rulelist) + '|')

    def align(self, source, target):
        (d, e) = self.perform_levenshtein(source, target)
        return e

if __name__ == '__main__':
    print("This file contains class definitions and cannot be run as a stand-alone script.")
    exit()
