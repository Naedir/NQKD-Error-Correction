#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 18:45:28 2019

@author: eddy
"""

'''
the complete cascade as described in the literature
'''


from error_and_compare import *
from Bob_Alice import *
from binary_protocol import *
from defs_for_cascade import *
import time as tm
import random as rd


'''
Step 1 of the cascade gets the first run of the correction done.
it returns size of blocks used in first run, 'corrected' blocks, as well as indecies of the blocks that were corrected
'''

class cascade:
    
    ## initial parameters which include Bob's and Alice's keys and QBER
    
    def __init__(self, Alices_key, Bobs_key, qber,k_times = 2,k_1 = 0.73,runs = 3):
        self.Alice_key = Alices_key
        self.Bob_key = Bobs_key
        self.qber = qber
        self.bits_lost = 0
        self.indecies = []  #index of blocks that were not corrected ()
        self.run = 0    #keeping track on how many runs of cascade there have been
        self.size_of_subblock = []  #keep track on what is the current size of a subblock
        self.seed = [] #array that will keep seeds for the permutation step
        self.parities = []  #keep track of all parities of Alice's key. since it's communicated over classical channel, this info is freely accessible
        self.k_1 = k_1
        self.k_multiplier = k_times
        self.binary_bits = []    #bits lost during Binary
        self.parity_bits = 0    #bits lost during parity of blocks exchange
        self.number_of_runs = runs
        self.Alice_split_keys = [None]*(self.number_of_runs+1)   #keep Alices split keys to save time on the backtracking step
        
        # indecies with error are structured as follows: 
        #       [cascade run[index with error]]
        self.indecies_with_error = []
        self.backaction_indecies = []
        self.backaction_path = []
        
        #path structure:
        #path = [[first cascade run: [path of the first index with error],[path of the second index with error], ...],
        #           [second cascade run: [path of the first index with error],[path of the second index with error], ...]]
        self.path = []
    '''
    Step 1 of the cascade gets the first run of the correction done.
    it returns size of blocks used in first run, 'corrected' blocks, as well as indecies of the blocks that were corrected
    '''

    def step_1(self):

        frame_size = len(self.Alice_key)
        if self.qber == 0:
            return print('no errors')
        #save the size of subblock:
        self.size_of_subblock.append(generate_k1(frame_size,self.k_1,self.qber))
        self.comparing()    #parity check followed by BINARY
    
    ###Now step two. it will be similar to step 1, but size of block is dofferent. it will include a step-back step afterwards.
    
    def step_i(self):
        # step_i has to be run after step_1. check if that's the case by checking if the run == 0
        
       
        if self.run == 0:   
            return print('step_1 must be run before step_i is run!')
#        
        frame = len(self.Alice_key)
        
        self.size_of_subblock.append(generate_k(frame_size = frame,kn_1 = self.size_of_subblock[self.run-1],k_factor = self.k_multiplier))
        self.comparing()
    #this function will be repeated, so make it a separate function
    def comparing(self):
        #each all of this finction is a new run of the cascade, therefore append lists that need to be organised in the 'run' order
        
        self.binary_bits.append(0)
        self.seed.append(100*rd.random())
        self.indecies.append([])
        self.path.append([])
        self.backaction_indecies.append([])
        self.backaction_path.append([])
        self.indecies_with_error.append([])
        
        #Shuffle Alice and Bob's keys:
        
        shuffle(self.Alice_key,self.seed[self.run])   #at this stage the value of run isn't updated yet
        shuffle(self.Bob_key,self.seed[self.run])
        #now key1 and key2 are Alice's and Bob's keys split into 'k' sized blocks
        key1 = list(div(self.Alice_key,self.size_of_subblock[self.run]))
        key2 = list(div(self.Bob_key,self.size_of_subblock[self.run]))
        self.Alice_split_keys[self.run] = key1

        number_of_blocks = len(key1)
        corrected_block_Alice = []
        corrected_block_Bob = []
        Alice_parities = [None]*number_of_blocks #this will keep track on parities of each block
        Bob_parities = [None]*number_of_blocks #this will keep track on parities of each block
        # check parities of each block:
        #0 means even, 1 means odd
        #also make an array of indecies, which have a mismatch in parity
        indecies = []
        for i in range(number_of_blocks):
            Alice_parities[i] = parity(key1[i])
            Bob_parities[i] = parity(key2[i])
            self.bits_lost += 1 #each time you reveal 1 bit of information
            self.parity_bits += 1
            
            if Alice_parities[i] != Bob_parities[i]:
                self.indecies_with_error[self.run].append(i)
                indecies.append(i)
            else:
                self.indecies[self.run].append(i)

        #perform binary on each block, whose indices you just found
        if len(indecies) != 0:
            counter = -1
            for i in indecies:
                counter += 1
                data = binary(key1[i],key2[i])
                key2[i] = data[1]
                path = data[3]
                # print(counter)
                
                self.path[self.run].append([path])
                # self.path[self.run][counter] = path
                self.bits_lost += data[2]   - 1 #-1 in order to avoid double counting the errors
                self.binary_bits[self.run] += data[2] - 1

            self.Bob_key = flatten(key2)
        Alice_parities = list(Alice_parities)
        #unshuffle the keys:
        unshuffle(self.Alice_key,self.seed[self.run])   #at this stage the value of run isn't updated yet
        unshuffle(self.Bob_key,self.seed[self.run])
        self.parities.append(Alice_parities)
        self.run += 1
        # self.indecies_with_error.append(indecies)

    
    def backtracking(self):     #this will look for indecies to check after the first run for the look-back
        
        n_of_ind = 0
        bn = 0
        backaction_run = -1
        while 1:
            n_of_ind = 0
            backaction_run += 1
            for i in range(self.run):
                
                #apply the permutation from run 'i'to both Bob's key, and Bob's old key and Alice's key:
                shuffle(self.Bob_key, self.seed[i])
#                shuffle(self.Alice_key, self.seed[i])
                
                # divide Bob's key into blocks from k_i:
                key1 = list(div(self.Bob_key, self.size_of_subblock[i]))  
                #key1 is Bob's current key
                key3 = self.Alice_split_keys[i]       #key1 is Alice's key
                number_of_blocks = len(key1)
                #check which indices revealed a new error:
                new_parities = [None]*number_of_blocks      #this will keep track on parities of each block
                # check parities of each block:
                #0 means even, 1 means odd
                #also make an array of indecies, which have a mismatch in parity
                indecies = []

                for j in range(number_of_blocks):
                    new_parities[j] = parity(key1[j])
                    if new_parities[j] != self.parities[i][j]:
                        indecies.append(j)
                
                self.backaction_indecies[i] += (indecies)
                #Now check parities of Bob's current key in those indecies:
                index = -1
                for l in indecies:
                    index += 1
                    data = binary(key3[l],key1[l])
                    key1[l] = data[1]
                    self.backaction_path[i].append(data[3])
                    self.bits_lost += data[2] -1
                    self.binary_bits[i] += data[2] - 1

                n_of_ind += len(indecies)
                #if no bits were corrected, update Bob's key and terminate back-tracking             
                if i == (self.run - 1) and n_of_ind == 0:
                    bn += 1
                    if bn == 2:
                        key1 = list(flatten(key1))
                        self.Bob_key = list(key1)
                        unshuffle(self.Bob_key, self.seed[i])
                        return

                #now since the Bob's key is fixed more, update it
                key1 = list(flatten(key1))
                self.Bob_key = list(key1)

                unshuffle(self.Bob_key, self.seed[i])

    ''' Now the Big Boy time. get the whole cascade going!!!!!'''
    def full_cascade(self):
#        self.indecies = [None]*4
        t1 = tm.process_time()
        self.step_1()
        rounds = 1
#        print(f'Time taken for the run number {rounds} is:\n%4f' %(tm.process_time() - t1),'s\n')
        for i in range(self.number_of_runs):
            rounds += 1
            t2 = tm.process_time()
            self.step_i()
#            print(f'time for step i = {tm.process_time() - t2}')
            t3 = tm.process_time()
            self.backtracking()
#            print(f'time backtracking = {tm.process_time() - t3}\n')


'''
This will be a cascade for charlie(s), used in multi-user cascades 
'''

class multi_cascade:
    
    ''' The last argument is **kwarg argument. it will consist of keys of each Bob'''
    
    def __init__(self, alice_key, qber, alice_split_key, seeds, parities, size_of_subblocks, indecies_with_error, paths, backaction_indecies, backaction_path, *charlie_key):
        self.Alice_key = alice_key
        self.number_of_charlies = len(charlie_key)
        #define Bobs keys:
        # self.Charlie_key = [None] * len(charlie_key_and_seed.key)
        self.qber = qber
        self.Alice_split_keys = alice_split_key
        self.seed = seeds
        self.size_of_subblock = size_of_subblocks
        self.run = 0
        self.bits_lost = [0] * self.number_of_charlies
        self.number_of_runs = 3
        # the important thing here is that we can reuse parities from previous cascade run, so that we don't use any more bits for the parity checks
        self.parities = parities
        self.indecies_with_error = list(indecies_with_error)
        self.paths = paths
        #this will keep a number of bits saved when performing binaty. bits will be added here, when the same subblock as before is being
        #performed binary on, for as long as the path matches previous path.

        self.path = paths
        self.indecies = []
        self.parity_bits = 0
        self.backaction_indecies = backaction_indecies
        self.backaction_path = backaction_path 
        self.binary_bits = [0] * self.number_of_charlies
        self.saved_bits_binary = [0] * self.number_of_charlies
        
        self.Charlie_key = [None]*self.number_of_charlies
        for i in range(self.number_of_charlies):
            self.Charlie_key[i] = charlie_key[i]
        # self.overall_bits_lost = sum(self.bits_lost) - sum(saved_bits_binary)
        
    #define a function that will check how many bits can be saved during a binary process:
        
    def save_bits(self,path, old_path):
        saved_bits = 0
        count = -1
        for i in path:
            count +=1
            try:
                old_path[count] and path
                
            except IndexError:
                return saved_bits
            if i == old_path[count]:
                saved_bits += 1
            else:
                return saved_bits
                # break
        return saved_bits          
    '''
    Step 1 of the cascade gets the first run of the correction done.
    it returns size of blocks used in first run, 'corrected' blocks, as well as indecies of the blocks that were corrected
    '''

    def step_1(self,num):
        frame_size = len(self.Alice_key)
        if self.qber == 0:
            return print('no errors')
        #save the size of subblock:

        self.comparing(num)    #parity check followed by BINARY
    
    ###Now step two. it will be similar to step 1, but size of block is dofferent. it will include a step-back step afterwards.
    
    def step_i(self,num):
        # step_i has to be run after step_1. check if that's the case by checking if the run == 0
        
       
        if self.run == 0:   
            return print('step_1 must be run before step_i is run!')
#        
        frame = len(self.Alice_key)
        
        self.comparing(num)
    #this function will be repeated, so make it a separate function
    def comparing(self, num):

        self.indecies.append([])
        #Shuffle Alice and Bob's keys:
        
       #at this stage the value of run isn't updated yet
        shuffle(self.Charlie_key[num],self.seed[self.run])
        #now key1 and key2 are Alice's and Bob's keys split into 'k' sized blocks
        key1 = self.Alice_split_keys[self.run]
        key2 = list(div(self.Charlie_key[num],self.size_of_subblock[self.run]))
        self.Alice_split_keys[self.run] = key1

        number_of_blocks = len(key1)
        corrected_block_Alice = []
        corrected_block_Charlie = []
        Alice_parities = [None]*number_of_blocks #this will keep track on parities of each block
        Charlie_parities = [None]*number_of_blocks #this will keep track on parities of each block
        # check parities of each block:
        #0 means even, 1 means odd
        #also make an array of indecies, which have a mismatch in parity
        indecies = []
        for i in range(number_of_blocks):
            Alice_parities[i] = parity(key1[i])
            Charlie_parities[i] = parity(key2[i])
            # self.bits_lost += 1 #each time you reveal 1 bit of information
            # self.parity_bits += 1
            
            if Alice_parities[i] != Charlie_parities[i]:
                indecies.append(i)
                
            else:
                self.indecies[self.run].append(i)

        #perform binary on each block, whose indices you just found
        if len(indecies) != 0:
            counter = -1
            for i in indecies:
                counter += 1
                data = binary(key1[i],key2[i])
                key2[i] = data[1]
                path = data[3]
                # print(counter)

                self.bits_lost[num] += data[2]  - 1  #-1 in order to avoid double counting the errors
                self.binary_bits[num] += data[2] - 1
                
                if i in self.indecies_with_error[self.run]:
                    index = self.indecies_with_error[self.run].index(i)
                    self.saved_bits_binary[num] += self.save_bits(path,self.path[self.run][index])
                else:
                    self.indecies_with_error[self.run].append(i)
                    self.path[self.run].append([path])
                    

            self.Charlie_key[num] = flatten(key2)
        # Alice_parities = list(Alice_parities)
        #unshuffle the keys:
        #at this stage the value of run isn't updated yet
        unshuffle(self.Charlie_key[num],self.seed[self.run])
        
        # self.parities.append(Alice_parities)
        self.run += 1
        # self.indecies_with_error.append(indecies)

    
    def backtracking(self, num):     #this will look for indecies to check after the first run for the look-back
        
        n_of_ind = 0
        bn = 0
        backaction_run = -1
        while 1:
            backaction_run += 1
            n_of_ind = 0
            for i in range(self.run):
                #apply the permutation from run 'i'to both Bob's key, and Bob's old key and Alice's key:
                shuffle(self.Charlie_key[num], self.seed[i])
#                shuffle(self.Alice_key, self.seed[i])
                
                # divide Bob's key into blocks from k_i:
                key1 = list(div(self.Charlie_key[num], self.size_of_subblock[i]))        #key1 is Bob's current key
                key3 = self.Alice_split_keys[i]       #key1 is Alice's key
                number_of_blocks = len(key1)
                #check which indices revealed a new error:
                new_parities = [None]*number_of_blocks      #this will keep track on parities of each block
                # check parities of each block:
                #0 means even, 1 means odd
                #also make an array of indecies, which have a mismatch in parity
                indecies = []
                path = []
                
                for j in range(number_of_blocks):
                    new_parities[j] = parity(key1[j])
                    if new_parities[j] != self.parities[i][j]:
                        indecies.append(j)
                                
                #Now check parities of Bob's current key in those indecies:
                index = -1
                
                self.backaction_indecies[i] += (indecies)
                for l in indecies:
                    index += 1
                    data = binary(key3[l],key1[l])
                    key1[l] = data[1]
                    
                    self.backaction_path[i].append(data[3])
                    self.bits_lost[num] += data[2] - 1
                    self.binary_bits[num] += data[2] - 1
                    path = data[3]
                    
                    ## saving bits bit:

                    if l in self.backaction_indecies[i]:
                        index = self.backaction_indecies[i].index(l)
                        self.saved_bits_binary[num] += self.save_bits(path,self.backaction_path[i][index])

                n_of_ind += len(indecies)
                #if no bits were corrected, update Bob's key and terminate back-tracking             
                if i == (self.run - 1) and n_of_ind == 0:
                    bn += 1
                    if bn == 2:
                        key1 = list(flatten(key1))
                        self.Charlie_key[num] = list(key1)
                        unshuffle(self.Charlie_key[num], self.seed[i])
                        return

                #now since the Bob's key is fixed more, update it
                key1 = list(flatten(key1))
                self.Charlie_key[num] = list(key1)

                unshuffle(self.Charlie_key[num], self.seed[i])

    ''' Now the Big Boy time. get the whole cascade going!!!!!'''
    def full_cascade(self):
#        self.indecies = [None]*4
        t1 = tm.process_time()
        
        for j in range(self.number_of_charlies):
            self.step_1(j)
            rounds = 1
    #        print(f'Time taken for the run number {rounds} is:\n%4f' %(tm.process_time() - t1),'s\n')
            for i in range(self.number_of_runs):
                rounds += 1
                t2 = tm.process_time()
                self.step_i(j)
    #            print(f'time for step i = {tm.process_time() - t2}')
                t3 = tm.process_time()
                self.backtracking(j)
    #            print(f'time backtracking = {tm.process_time() - t3}\n')
            self.run = 0

