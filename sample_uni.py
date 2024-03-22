# -*- coding: utf-8 -*-
"""
Sample universities from a range of rankings such that countries and degrees of focus are 
distributed as evenly as possible

Explanation of focus: https://support.qs.com/hc/en-gb/articles/360021876820-QS-Institution-Classifications

@author: K. Nolle
"""

import pandas as pd
import random
import math

rank_min = 1
rank_max = 100
sample_size = 40

# Read PDF with rankings
df_rankings = pd.read_excel('data/2024_QS_World_University_Rankings.xlsx', header=3)
df_rankings["qs_ranking"] = df_rankings["rank display"].str.extract('(\d+)')
df_rankings["qs_ranking"] = pd.to_numeric(df_rankings["qs_ranking"])
df_rankings = df_rankings[["qs_ranking", "institution", "focus","location"]]

# Filter for ranking range
df_rankings = df_rankings[(df_rankings["qs_ranking"] >= rank_min) & (df_rankings["qs_ranking"] <= rank_max)]

# Randomly sample the same number of universities from each country
n_locations = len(df_rankings[["location", "focus"]].drop_duplicates())
df_sample = df_rankings.groupby(["location", "focus"]).sample(n=math.ceil(sample_size/n_locations), replace=True)
df_sample = df_sample.drop_duplicates()

# Randomly drop rows if too many were sampled
if len(df_sample) > sample_size:
    drop_indices = random.sample(df_sample.index.tolist(), len(df_sample) - sample_size)
    df_sample = df_sample.drop(drop_indices)
    
# Randomly sample from remaining universities if not enough were sampled
elif len(df_sample) < sample_size:
   
    sample_indices = df_sample.index.tolist()
    remaining_indices = [x for x in df_rankings.index.tolist() if x not in sample_indices]
    
    sample_indices = sample_indices + random.sample(remaining_indices, sample_size - len(df_sample))
    df_sample = df_rankings.loc[sample_indices]

df_sample = df_sample.reset_index(drop=True)
df_sample = df_sample.sort_values("qs_ranking")

# Add columns to fill in
df_sample = df_sample.reindex(df_sample.columns.tolist() + ["continent", 
                                                            "year_established", 
                                                            "private_public", 
                                                            "type",
                                                            "strategy_start",
                                                            "strategy_end",
                                                            "filename"], axis=1)

# Output results
df_sample.to_csv(f"data/university_list_{rank_min}-{rank_max}.csv", index=False)

