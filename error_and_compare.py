#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 19:01:21 2019

@author: eddy
"""
import random as rd
from defs_for_cascade import *
import numpy as np

### now a function that will divide the key into k_n seized blocks:
def div(key,k_n):
    number_of_blocks = int(np.ceil(len(key) / k_n))
    
    A_n = [None] * number_of_blocks
    index = 0
    for i in range(number_of_blocks):
        starting_index = i*k_n
        end_index = starting_index + k_n
        A_n[index] = key[starting_index:end_index:]
        index += 1
    
    return A_n

#def div(key, k_n):
#    number_of_blocks = int(len(key) / k_n)
#    
#    #make number_of_blocks number of arrays called A_1...A_n etc:
#    
#    A_n = {}
#    if number_of_blocks > 1:
#        if int(len(key)) % number_of_blocks == 0:       # the if statement ensures, that if  there is a reminder key 
#                                                        #after dividing into n blocks, the remainder will have it's own directory entry
#            for i in range(number_of_blocks):
#                A_n[f"A_{i+1}"] = [None]* k_n
#        else:
#            for i in range(number_of_blocks+1):
#                A_n[f"A_{i+1}"] = [None]*k_n
#        
#        index_propagator = 0    #this will keep track on the index number of the key
#        
#        for i in range(len(A_n)-1):
#            for j in range(k_n):
#                A_n[f"A_{i+1}"][j] = (key[index_propagator])
#                index_propagator += 1   
#        A_n[f"A_{int(len(A_n))}"] = list((key[index_propagator::]))
#    else:
#        A_n['A_1'] = list(key)
#    
#    return A_n

## a function to check for parity
def parity(array):
    return (sum(array) % 2)

## make a function that splits key into two parts
def split(key):
    Bob_key = [None]*2
    Bob_key[0] = ([x for x in key[:int(len(key)/2)]])
    Bob_key[1] = ([x for x in key[int(len(key)/2)::]])
    
    return Bob_key

## make function that applies one error to first or second half of the key
def single_error(key):
    data = split(key)
    first_half_Bob = data[0]
    second_half_Bob = data[1]
    
    #applying an error in a random place in an array
    def apply(arr):
        ind = rd.randint(0,len(arr)-1)
        arr[ind] = abs(arr[ind] - 1)
        return arr
    
    #now apply the error to either first or a second half:
    if rd.randint(0,1) == 0:
        first_half_Bob = apply(first_half_Bob)
    else:
        second_half_Bob = apply(second_half_Bob)
    Bob_key = first_half_Bob + second_half_Bob
    return Bob_key

## make a function that compares parity of a given half of a key:
    #it takes in two keys (identical), then applies error to one of them and checks parity
def compare_parity(key, key2): # key = Bob's key, key2 = Alice's key
    Bob_key = split(key)
    Alice_key = split(key2)
    
    # checking bit:
    '''it will return 'right' or 'left', which will be analogous to the half of the key that contains an error
    it will alsoremove the last bit from the half that contains an error
    'left' has an index 0, and 'right' has an index 1'''
    
    def check(Bob_ar, Alice_ar):

        if parity(Bob_ar[0]) == parity(Alice_ar[0]):
            return 1    #1 means right
        return 0    #0 means left

        

    result = check(Bob_key, Alice_key)
    
    return Bob_key, Alice_key, result
