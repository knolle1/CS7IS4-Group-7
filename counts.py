# -*- coding: utf-8 -*-
"""
Read tokens and performs the following pre-processing steps:
    - count the frequency of uni- and bi-grams
    - removes n-grams that only consist of numbers (to avoid using page numbers etc.)
    - filter out n-grams that are only 1 character long
    - calculate the relative frequencies
    - only keep the 20 most frequent n-grams per document

@author: K. Nolle
"""

from collections import Counter
import pandas as pd
import os
import json


input_directory = './data/tokenized-txt'
output_directory = './data'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    
    
def extract_n_grams(n, k, input_directory, save_as):
    df_all = pd.DataFrame()
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            
            input_path = os.path.join(input_directory, filename)
            
            with open(input_path, 'r', encoding='utf-8') as file:
                uni_grams = json.load(file)
                
            # Skip empty files
            if len(uni_grams) > 0:
                print(f"Counting {filename} ...")
                
                if n == 1:
                    n_grams = uni_grams
                elif n == 2:
                    # Generate bi-grams
                    n_grams = [word1+' '+word2 for word1, word2 in zip(uni_grams[:-1], uni_grams[1:])]
                
                # Count n-grams
                n_grams = pd.Series(Counter(n_grams)).sort_values(ascending=False)
                
                # Remove n-grams that are only numbers
                n_grams = n_grams[n_grams.index.str.isnumeric() == False]
                
                # Filter out n-grams that are only 1 letter
                n_grams = n_grams[n_grams.index.str.len() > 1]
                
                # Calculate relative frequency
                n_grams = n_grams / len(n_grams)
                
                # Filter for the top k n-grams
                threshold = n_grams[k-1]
                n_grams = n_grams[n_grams >= threshold]
                
                # Add to dataframe
                n_grams.name = filename
                df_all = pd.concat([df_all, pd.DataFrame(n_grams).transpose()])
                
    # Fill NaNs with 0
    df_all = df_all.fillna(0)
    
    # Save results
    print(f"Saving results to {save_as} ...")
    df_all.to_csv(save_as)


extract_n_grams(1, 20, input_directory, os.path.join(output_directory, 'uni-grams_rel-frequ.csv'))
extract_n_grams(2, 20, input_directory, os.path.join(output_directory, 'bi-grams_rel-frequ.csv'))