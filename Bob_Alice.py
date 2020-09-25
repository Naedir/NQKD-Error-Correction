#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 13:13:39 2019

@author: eddy
"""

from qutip import *
import matplotlib as plt
import numpy as np
import random as rd
import time as tm
from numpy import random as rdi


''' Define a class called 'Bob". it will represent a receiver of a quantum bit. later on there will be a sender defined as 'Alice'.
Bob will have a list of 0s and 1s (a key), a method for introducing noise  and some error correction methods'''


class Bob:

    #    def __init__(self,):       ## wil leave it blank for now, as dont really know what to put as initial conditions

    """ 
    the following method will produces a key (random list of 1s and 0s). the 'size' determines how many bits it'll have
    use it if you want a random key to be generated in an instance of the class. 
    if you want to give a particular key to the Bob, use key_import
    """

    def key_creation(self, size):

        self.key = list(rdi.randint(low = 0,high = 2,size = size))
        
    '''
    key_import assigns a given string (key_to_import) to the instance of the class as a 'key'
    '''

    def key_import(self, key_to_import):
        self.key = []
        self.key = key_to_import.copy()

    ''' create a function that will introduce an error to the key. Key with errors will be assigned an atribute key_modified '''

    # p is a parameter, which is equal to the probability that a bit will be flipped (1 --> 0, 0 --> 1)
    def apply_error(self, p):
                                # p E {0,1}
                                
        #number of bits to be flipped:
        
        size_of_key = len(self.key)
        n = int(p * size_of_key)
        indecies = np.random.choice(np.arange(size_of_key),n,replace = False)
        count_of_errors = 0
        for i in indecies:
            self.key[i] = abs(self.key[i] - 1)
            count_of_errors += 1
        self.qber = count_of_errors/size_of_key
#        
#        try:
#            self.key
#            # create an atribute that will hold a noisy key
#            self.key_modified = self.key.copy()
#            # this will keep track on the amount of errors. it will be used to calculate QBER
#            count_of_errors = 0
#            for i in range(len(self.key)):
#                if rd.random() <= p:
#                    # this line flips 0 to 1, and 1 to 0
#                    self.key_modified[i] = abs(self.key_modified[i]-1)
#                    count_of_errors += 1
#                else:
#                    continue
#            self.qber = count_of_errors/(len(self.key))
#            self.n_of_errors = count_of_errors
#        except AttributeError:
#            print('atribute \'key\' does not exist.\nuse self. key_creation or self.key_import to create a \'key\' attribute')

        # QBER is a a 'qubit error rate'. it is defined as the ratio of wrong bits to the total number of bits of the raw key

    ''' Now make a more complicated code, that will modify a key to a given QEBR. it means, that it will take a desirable QEBR, and will keep applying errors 
    until desired QEBR is reached. there can be small differences between desired QEBR and actual QEBR, because not all sizes of key are able to give every
    value of QEBR'''

    def apply_error2(self, rate):  # rate is a desired value of QEBR
        try:
            self.key
            # this will keep track on the amount of errors. it will be used to calculate QBER
            count_of_errors = 0
            self.n_of_errors = count_of_errors
            self.qber = count_of_errors/(len(self.key))
            size_of_key = len(self.key)
            used_index = []
            index = rd.randint(0, size_of_key-1)
            while rate > self.qber:

                count_of_errors += 1
                # this keeps updating QBER
                self.qber = count_of_errors/(len(self.key))
                self.n_of_errors = count_of_errors
                while 1:
                    # this generates randomly index of the key to be changed, aka make an error in 'index' entry
                    index = rd.randint(0, size_of_key-1)
                    ' To make sure that no index values are reused, keep a track of all used indexes:'
                    if index in used_index:
                        continue
                    else:
                        # this line flips 0 to 1, and 1 to 0
                        self.key[index] = abs(
                            self.key[index]-1)
                        ' To make sure that no index values are reused, keep a track of all used indexes:'
                        used_index.append(index)
                        break
        except AttributeError:
            print('atribute \'key\' does not exist.\nuse self. key_creation or self.key_import to create a \'key\' attribute')

        #####################################################
        # here make a method that will take a qubit ( in a computational basis) and measures it
        # the measurement can be taken from the summer project's code
        # use qutip toolkit
        #####################################################

    '''help-like function. just containing some basic info on methods contained in the class'''
    
    
    def guide(self, choice='alll'):
        if choice == 'alll':
            print(
'================= \nMethods: \nkey_creation \nkey_import \napply_error \napply_error2')
        elif choice == 'apply_error':
            print('================= \napply_error(p) goes thrpough each entry of the self.key list. \np is a parameter between 0 and 1, and is equal to the probability that n\'th element will flip\n(flip means 0 goes to 1, and 1 goes to 0)')
            print('key with error is saved as a new attribute called \'key_modified\'. QBER is also calculated and saved as an attribute \'qber\'')
        elif choice == 'apply_error2':
            print('================= \napply_error2 is a second way of applying errors to a key. it takes a desired QBER as a parameter, and flips a random bit from a code until a desired QBER is reached.')
            print('key with error is saved as a new attribute called \'key_modified\'. QBER is also calculated and saved as an attribute \'qber\'')
        else:
            print('Method doesn\'t exist')

class Alice:

    #    def __init__(self,):       ## wil leave it blank for now, as dont really know what to put as initial conditions

    """ 
    the following method will produces a key (random list of 1s and 0s). the 'size' determines how many bits it'll have
    use it if you want a random key to be generated in an instance of the class. 
    """

    def key_creation(self, size):

        self.key = []
        for i in range(size):
            self.key.append(rd.randint(0, 1))
## flatten list function 
def flatten(ar):
    flatten_list = []
    for sublist in ar:
        for item in sublist:
            flatten_list.append(item)
    return flatten_list