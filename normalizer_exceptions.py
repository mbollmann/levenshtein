#!/usr/bin/python
# -*- coding: utf-8 -*-

class NormalizerException(Exception):
    pass

class InitError(NormalizerException):
    pass

class ProgramExitRequest(NormalizerException):
    pass

if __name__ == '__main__':
    print("This file contains class definitions and cannot be run as a stand-alone script.")
    exit()
