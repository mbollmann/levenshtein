#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, math
import argparse
from collections import defaultdict
from operator import itemgetter
from itertools import tee, izip
from WeightedLevenshtein import LevenshteinWeights
from Levenshtein import LevenshteinAligner

def groupwise(iterable, n=2):
    tees = tee(iterable, n)
    for i in range(n):
        for j in range(i):
            next(tees[i], None)
    return izip(*tees)

def calc_avg_stddev(result):
    avg = sum(result) * 1.0 / len(result)
    var = map(lambda x: (x - avg)**2, result)
    stddev = math.sqrt(sum(var) * 1.0 / len(var))
    return (avg, stddev)

def make_ruleset_ngrams(rs, n):
    ngrams = [[x] for x in rs]
    for i in range(1,n):
        for x in groupwise(rs, n=i+1):
            ngrams.append(x)
    return ngrams

class PMILevenshtein(object):
    """Class to train weights using PMI algorithm."""
    weights = None
    pairs   = {}
    alignments = {}
    ngrams  = 1

    convergence_quota = 0.01
    min_freq_divisor = 6.293

    # how fast weights are adjusted
    learning_rate = 0.2

    # Current distance formula used:
    # (max_pmi - pmi) / max(max_pmi - pmi)

    def __init__(self):
        self.weights = LevenshteinWeights()
        self.weights.setDirected(True)
        self.pairs = defaultdict(int)

    def add_pair(self, source, target):
        self.pairs[(source, target)] += 1

    def get_pair_count(self):
        return sum(map(itemgetter(1), self.pairs.items()))

    def perform_alignments(self):
        alignments = {}
        leven = LevenshteinAligner(weights=self.weights)
        for pair in self.pairs:
            alignments[pair] = leven.align(*pair)
        return alignments

    def find_ngram_weights(self, n=2):
        def make_ruleset_ngrams(rs, n):
            ngrams = [[x] for x in rs]
            for i in range(1,n):
                for x in groupwise(rs, n=i+1):
                    ngrams.append(x)
            return ngrams

        a = 0.5 ### additive smoothing
        alignments = self.alignments
        lhs = defaultdict(int)
        ngrams = defaultdict((lambda: defaultdict(int)))
        for (pair, rulesets) in alignments.iteritems():
            value = self.pairs[pair]
            for ruleset in rulesets:
                for ngram_rule in make_ruleset_ngrams(ruleset, n=n):
                    source = ''.join(map(itemgetter(0), ngram_rule))
                    target = ''.join(map(itemgetter(1), ngram_rule))
                    # hacky as can be
                    if source != '<eps>':
                        source = source.replace('<eps>','')
                    if target != '<eps>':
                        target = target.replace('<eps>','')
                    lhs[source] += value
                    ngrams[source][target] += value
        weights = {}

        ### Idea: too unfrequent rule sources get penalized by
        ### assigning a minimum frequency level that is used for the
        ### calculation
        minlevel = self.get_pair_count() / self.min_freq_divisor

        for (source, tdict) in ngrams.iteritems():
            probbase = max(lhs[source], minlevel)
            for (target, freq) in tdict.iteritems():
                ### conditional probability p(RHS|LHS) with additive smoothing
                prob = ((freq * 1.0) + a) / (probbase + (a * len(tdict)))
                dist = -math.log(prob)
                weights[(source,target)] = dist
        return weights

    def collect_rules_by_freq(self, alignments):
        rules_by_freq = defaultdict(int)
        for (pair, rulesets) in alignments.iteritems():
            value = self.pairs[pair]
            for ruleset in rulesets:
                for rule in make_ruleset_ngrams(ruleset, n=self.ngrams):
                    source = ''.join(map(itemgetter(0), rule))
                    target = ''.join(map(itemgetter(1), rule))
                    # hacky as can be
                    if source != '<eps>':
                        source = source.replace('<eps>','')
                    if target != '<eps>':
                        target = target.replace('<eps>','')
                    rules_by_freq[(source, target)] += value
        return rules_by_freq

    def calculate_probabilities(self, rules):
        p_rule, p_source, p_target = {}, {}, {}
        freq_source, freq_target = defaultdict(int), defaultdict(int)
        total_alignments = sum(rules.values())

        for (rule, freq) in rules.iteritems():
            p_rule[rule] = float(freq) / total_alignments
            (source, target) = rule
            freq_source[source] += freq
            freq_target[target] += freq

        total_source = sum(freq_source.values())
        for (source, freq) in freq_source.iteritems():
            p_source[source] = float(freq) / total_source

        total_target = sum(freq_target.values())
        for (target, freq) in freq_target.iteritems():
            p_target[target] = float(freq) / total_target

        return (p_rule, p_source, p_target)

    def calculate_distances(self, rules, pr, ps, pt):
        method = 'pmi'
        if method=='pmi':
            pmi = {}
            for rule in rules:
                (source, target) = rule
                pmi[rule] = math.log(pr[rule] / (ps[source]*pt[target]), 2)
            max_pmi  = max(pmi.values())
            max_dist = max_pmi - min(pmi.values())

            dist = {}
            for rule in rules:
                if max_dist == 0:  # edge case -- shouldn't happen on real data
                    dist[rule] = sys.maxint
                else:
                    dist[rule] = (max_pmi - pmi[rule]) / max_dist
        elif method=='mine':
            dist = {}
            for rule in rules:
                (source, target) = rule
                if source==target:
                    dist[rule] = 0.0
                else:
                    dist[rule] = 1.0 - (pr[rule] / pt[target])


        return dist

    def adjust_weights(self, distances):
        factor = self.learning_rate
        getw = self.weights.get_weight
        setw = self.weights.set_weight
        diffs = []
        for (rule, dist) in distances.iteritems():
            (source, target) = rule
            old_weight   = getw(source, target)
            new_weight   = old_weight * (1.0 - factor)
            new_weight  += dist * factor
            diffs.append(abs(old_weight - new_weight))
            setw(source, target, new_weight)
        return diffs

#    def convergence_reached(self, align1, align2):
#        mismatch = 0
#        for (pair, rulesets1) in align1.iteritems():
#            rulesets2 = align2[pair]
#            if sorted(rulesets1) != sorted(rulesets2):
#                mismatch += self.pairs[pair]
#
#        total_pairs = sum(self.pairs.values())
#        if (float(mismatch)/total_pairs) > self.convergence_quota:
#            return False
#        return True

    def train(self, log_to=sys.stderr):
        def log(msg):
            if log_to:
                log_to.write(msg)

        for i in range(1, 20):
            # calculate new alignments
            log("[PMI] Performing cycle %2i..." % i)
            alignments = self.perform_alignments()
            # derive rule frequency statistics
            rules = self.collect_rules_by_freq(alignments)
            # calculate rule and character probabilities
            (pr, ps, pt) = self.calculate_probabilities(rules)
            # calculate distance values based on PMI
            distances = self.calculate_distances(rules, pr, ps, pt)
            # adjust edit distance weights
            delta = self.adjust_weights(distances)
            avg_delta = sum(delta) * 1.0 / len(delta)
            log(" avg delta: %.4f\n" % avg_delta)
            # if edit distance weights have not changed significantly,
            # convergence is reached
            if avg_delta <= self.convergence_quota:
                log("[PMI] Convergence reached.  Stopping.\n")
                break
        else:
            log("[PMI] Maximum number of iterations reached.  Stopping.\n")

        log("[PMI] Generating final alignments...")
        self.alignments = self.perform_alignments()
        log(" done.\n")

if __name__ == '__main__':
    print("This file contains class definitions and cannot be run as a stand-alone script.")
    exit()
