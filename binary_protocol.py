#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 21:17:59 2019

@author: eddy
"""

from Bob_Alice import *
from error_and_compare import *
import time
####################################################

'''
This will be the heart of the protocol. a function that takes in  two keys, (one with a single error)
and outputs two identical keys by performing a BINARY
'''

def binary(key1, key2):
    #key1 is Alice's key, assumed to be the correct key, whereas key2 is Bob's key that has a single error
    
    data = compare_parity(key1,key2)    #just comparing parities of two halves of the keys and checking parity. data consists of the two keys (split in half)
                                        #as well as the side at which the parity doesn't match
    Alice_key = data[0]
    Bob_key = data[1]
    side = data[2]
    index = 0       #this will keep a track on which block to split further. everytime the 'left' side gets split, index stays the same. everytime the 'right'
                    #block gets split 'index' increases by 1. this way always the 'index' index of the key gets split.
    
    #keep track of each 'left' or 'right'
    number_of_steps = 1
    previous_Alice = []
    
    # keep a track of what path the binary took
    
    path = []
    path.append(side)
    while 1: #this ensures, that the information exchange will go on until the size of last block is 1

        number_of_steps += 1
        if side == 0:
            previous_Alice = Alice_key
            data = compare_parity(Alice_key[index],Bob_key[index])
            Alice_block = data[0]
            Alice_key.pop(index)    #errase the block that gets split
            '''the next two lines just add the split block in the place of the original block'''
            Alice_key.insert(index, Alice_block[0])
            Alice_key.insert(index+1, Alice_block[1])
            
            Bob_block = data[1]
            Bob_key.pop(index)  #errase the block that gets split
            '''the next two lines just add the split block in the place of the original block'''
            Bob_key.insert(index, Bob_block[0])
            Bob_key.insert(index+1, Bob_block[1])
            side = data[2]  #update the side
            path.append(side)
            
        elif side == 1:
            previous_Alice = Alice_key
            index = index + 1
           #print(Bob_key[index])
            data = compare_parity(Alice_key[index],Bob_key[index])
            Alice_block = data[0]
            Alice_key.pop(index)    #errase the block that gets split
            '''the next two lines just add the split block in the place of the original block'''
            Alice_key.insert(index, Alice_block[0])
            Alice_key.insert(index+1, Alice_block[1])
            
            Bob_block = data[1]
            Bob_key.pop(index)  #errase the block that gets split
            '''the next two lines just add the split block in the place of the original block'''
            Bob_key.insert(index, Bob_block[0])
            Bob_key.insert(index+1, Bob_block[1])
            side = data[2]  #update the side
            path.append(side)
        else:
            print('something went wrong')
        
        if len(previous_Alice[index]) <=0:
#        if len(Bob_key[index]) <=1:
            break
    # keep a track of what path the binary took
    '''the output might contain an empty array. this needs to be errased before applying error correction'''
    Alice_key = [i for i in Alice_key if len(i) !=0]
    Bob_key = [i for i in Bob_key if len(i) !=0]
    #now correct the error. the error is in the in the Bob'skey, in the 'index' index
    try:
        Bob_key[index][0] = abs(Bob_key[index][0] - 1)
    except IndexError:
        Bob_key[index-1][0] = abs(Bob_key[index-1][0] - 1)
            

    # now the keys are ready and corrected, just make the 1-dimentional:
    Bob_key = flatten(Bob_key)
    Alice_key = flatten(Alice_key)   
        
    return Alice_key, Bob_key, number_of_steps, path
  #  return number_of_steps, all_steps
  
def discard_bits(key1, key2, sides):

    
    Alice_key = split(key1)
    Bob_key = split(key2)
    index = 0
    for i in sides:
        if i == 'left':
            try:
                Alice_key[index].pop()
                Alice_block = split(Alice_key[index])
                Alice_key.pop(index)
                Alice_key.insert(index, Alice_block[0])
                Alice_key.insert(index+1, Alice_block[1])
            except IndexError:
               pass
           
            try:
                Bob_key[index].pop()
                Bob_block = split(Bob_key[index])
                Bob_key.pop(index)
                Bob_key.insert(index, Bob_block[0])
                Bob_key.insert(index+1, Bob_block[1])
            except IndexError:
               pass
        else:
            index = index + 1
            try:
                Alice_key[index-1].pop()
                Alice_block = split(Alice_key[index])
                Alice_key.pop(index)
                Alice_key.insert(index, Alice_block[0])
                Alice_key.insert(index+1, Alice_block[1])
            except IndexError:
                pass
            try:
                Bob_key[index-1].pop()
                Bob_block = split(Bob_key[index])
                Bob_key.pop(index)
                Bob_key.insert(index, Bob_block[0])
                Bob_key.insert(index+1, Bob_block[1])  
            except IndexError:
                pass
    Bob_key = flatten(Bob_key)
    Alice_key = flatten(Alice_key)   
    return Alice_key, Bob_key
#
#for i in range(10000):
#    a = Alice()
#    a.key_creation(9)
#    b = Bob()
#    b.key_import(a.key)
#    key1 = a.key
#    key2 = list(b.key)
#    key2 = single_error(key2)
#    data = binary(key1, key2)
#    if data[0] != data[1]:
#        print('error')
##    