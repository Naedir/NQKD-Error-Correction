#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 18:04:36 2019

@author: eddy
"""

'''
First get the function that can shuffle and unshuffle bit strings randomly
'''
import random as rd
import numpy as np

'''it will be based on a seed. seed will be a number, which will determine how the numbers will shuffle
having the seed will allow for unshuffling the bits
since in a cascade each run has a different 'k' value, can use this as a seed
'''

def getperm(l,s):
    seed = s
    rd.seed(seed)
    perm = list(range(len(l)))
    rd.shuffle(perm)
    rd.seed() # optional, in order to not impact other code based on random
    return perm

def shuffle(l,s):
    perm = getperm(l,s)
    l[:] = [l[j] for j in perm]

def unshuffle(l,s):
    perm = getperm(l,s)
    res = [None] * len(l)
    for i, j in enumerate(perm):
        res[j] = l[i]
    l[:] = res


'''
make a function that calculates the number of bits in a block

according to literatire, the first round has 0.73/qber bits in a block, and k_n = 2 * k_(n-1)
'''
def generate_k1(frame_size,parameter,qber):
    k_1 = int(parameter / qber)
    '''also check if the new size isn't bigger than half of the frame size
    '''

    if k_1 > (int(frame_size/2)):
        return int(frame_size/2)
    elif k_1 >= frame_size:
         return int(frame_size/2)
    if k_1 < 2:
        return 2
    return k_1
def generate_k(frame_size, kn_1 = False, qber = False,k_factor=2):
    
    if qber != False and kn_1 == False:
        k_n = 0.73 / qber
    elif kn_1 != False:
        k_n = k_factor* kn_1
    else:
        print('Something went wrong with generating k_n....')
    '''also check if the new size isn't bigger than half of the frame size
    '''
    if k_n > (int(frame_size/2)):
        return int(frame_size/2)
    else:
        pass
    return int(k_n)

def stats(number,qberr):
    
    array_mean = []
    
    for i in range(number):
        b = Bob()
        a = Alice()
        a.key_creation(10000)
        b.key_import(a.key)
        b.apply_error2(qberr)
        k1 = a.key
        k2 = b.key_modified
        #k2 = single_error(k1)
        qb = b.qber
        d = cascade(k1,k2,qb)
        d.full_cascade()
        
        array_mean.append(d.bits_lost)
    mean = np.mean(array_mean)
    I = mean/(10000/d.size_of_subblock[0])
    return print(f'I(4) = {I}')

## flatten list function 
def flatten(ar):
    flatten_list = []
    for sublist in ar:
        for item in sublist:
            flatten_list.append(item)
    return flatten_list

def shannon(estimate):
    return (-estimate*np.log2(estimate) - (1 - estimate)*np.log2(1 - estimate))

