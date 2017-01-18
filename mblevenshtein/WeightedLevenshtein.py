#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, math, sys
from lxml import etree
from itertools import combinations

class XMLParamError(Exception):
    pass

class XMLTagError(XMLParamError):
    def __init__(self, tag, expected):
        self.param_tag = tag
        self.param_expected = expected

    def __str__(self):
        return ''.join(['Found tag "', self.param_tag, '", expected: ', self.param_expected])

class XMLMissingTagError(XMLParamError):
    def __init__(self, tag, expected):
        self.param_tag = tag

    def __str__(self):
        return ''.join(['Missing tag "', self.param_tag, '"'])

##################################################################
class LevenshteinWeights(object):
    accepted_types = ['directed','undirected']

    def __init__(self, filename="", fileformat="xml"):
        self.type         = ""
        self.weights      = {}
        self.epsilon      = '<eps>'
        self.default_identity_cost    = 0.0
        self.default_replacement_cost = 1.0
        self.default_insertion_cost   = 1.0
        self.default_deletion_cost    = 1.0
        if filename != "":
            self.loadParamFromFile(filename, fileformat)

    def setDirected(self, directed):
        self.type = 'directed' if directed else 'undirected'

    def isDirected(self):
        return (self.type == 'directed')

    def loadParamFromFile(self, filename, fileformat="xml"):
        if fileformat == "xml":
            self.loadParamFromXMLFile(filename)
        elif fileformat == "tabbed":
            self.loadParamFromNormaFile(filename)
        else:
            raise Exception("Unrecognized file format: %s" % fileformat)

    def loadParamFromXMLFile(self, filename):
        root = etree.parse(filename).getroot()
        if root.tag != "WeightSet":
            raise XMLTagError(root.tag, "WeightSet")

        self.type = root.get('type')
        if self.type not in self.accepted_types:
            raise XMLTagError("WeightSet[type=%s]"%self.type,
                              "WeightSet[type={%s}]"%'|'.join(self.accepted_types))

        tags = ('Replacement', 'Insertion', 'Deletion')
        (replacement_tag, insertion_tag, deletion_tag) = tags

        for child in root:
            if child.tag == replacement_tag:
                elem = (child.get('from'), child.get('to'))
            elif child.tag == insertion_tag:
                elem = (self.epsilon, child.get('of'))
            elif child.tag == deletion_tag:
                elem = (child.get('of'), self.epsilon)
            else:
                raise XMLTagError(child.tag, ' or '.join(tags))

            cost = float(child.get('cost'))
            self.weights[elem] = cost

    def loadParamFromNormaFile(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.rstrip().decode("utf-8")
                if not line:
                    continue
                (left, right, cost) = line.split("\t")
                self.weights[(left, right)] = float(cost)

    def make_xml_param(self):
        root = etree.Element("WeightSet")
        root.set('type', self.type)
        for (elem, cost) in self.weights.iteritems():
            (source, target) = elem
            if source == target:
                continue
            if source == self.epsilon:
                rule = etree.Element('Insertion')
                rule.set('of', target)
            elif target == self.epsilon:
                rule = etree.Element('Deletion')
                rule.set('of', source)
            else:
                rule = etree.Element('Replacement')
                rule.set('from', source)
                rule.set('to', target)
            rule.set('cost', str(cost))
            root.append(rule)
        return etree.tostring(root, encoding="utf-8")

    def reset_weights(self):
        self.weights = {}

    def return_weights(self):
        e = self.epsilon
        directed = self.isDirected()
        for (elem, cost) in self.weights.iteritems():
            if directed:
                (a, b) = elem
                yield (a, b, cost)
            else:
                for (a, b) in combinations(elem, 2):
                    yield (a, b, cost)
                    yield (b, a, cost)

    def get_weight(self, source, target):
        try:
            return self.weights[(source, target)]
        except KeyError:
            if source==target:
                return self.default_identity_cost
            elif source==self.epsilon:
                return self.default_insertion_cost
            elif target==self.epsilon:
                return self.default_deletion_cost
            else:
                return self.default_replacement_cost

    def set_weight(self, source, target, weight):
        self.weights[(source, target)] = weight


if __name__ == '__main__':
    print('This is not a stand-alone program.')
