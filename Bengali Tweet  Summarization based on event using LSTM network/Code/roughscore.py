# -*- coding: utf-8 -*-
"""roughscore.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qVYSXXWJt43nlzFKb4wfOKkoqUurfVDu
"""



!pip install rouge

import sys


# Increase recursion limit
sys.setrecursionlimit(10**6)



import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, Dense, Bidirectional, Concatenate, Dot, Activation, Embedding
from tensorflow.keras.models import Model
from rouge import Rouge
# Define the Rouge object
rouge = Rouge()

# load reference and summary texts
with open('decoderfile.txt', 'r') as f:
    ref_text = f.read()

with open('genrate.txt', 'r') as f:
    summary_text = f.read()
scores = rouge.get_scores(summary_text, ref_text, avg=True)
rougep1score = scores['rouge-1']['p']
rouger1score = scores['rouge-1']['r']
rougef1score = scores['rouge-1']['f']

print("ROUGE-1 pscore:", rougep1score)
print("ROUGE-1 rscore:" ,rouger1score)
print(f'ROUGE-1 fscore: {rougef1score}')
rougep2score = scores['rouge-2']['p']
rouger2score = scores['rouge-2']['r']
rougef2score = scores['rouge-2']['f']
print("ROUGE-2 pScore:", rougep2score)
print("ROUGE-2 rScore:", rouger2score)
print("ROUGE-2 fScore:", rougef2score)
with open("decoderfile.txt", "r", encoding="utf-8") as f:
    reference = f.read().strip()

with open("genrate.txt", "r", encoding="utf-8") as f:
    generated = f.read().strip()
# calculate ROUGE-L
scores = rouge.get_scores(generated, reference, avg=True)
rouge_lp = scores["rouge-l"]["p"]
rouge_lr = scores["rouge-l"]["r"]
rouge_lf = scores["rouge-l"]["f"]


# print the ROUGE-L score
print("ROUGE-L: p", rouge_lp)
print("ROUGE-L: r", rouge_lr)
print("ROUGE-L: f", rouge_lf)

from rouge import Rouge

# read the reference and generated summaries from files
with open("decoderfile.txt", "r", encoding="utf-8") as f:
    reference = f.read().strip()

with open("genrate.txt", "r", encoding="utf-8") as f:
    generated = f.read().strip()

# initialize Rouge
rouge = Rouge()

# calculate ROUGE-L
scores = rouge.get_scores(generated, reference, avg=True)
rouge_lp = scores["rouge-l"]["p"]
rouge_lr = scores["rouge-l"]["r"]
rouge_lf = scores["rouge-l"]["f"]


# print the ROUGE-L score
print("ROUGE-L: p", rouge_lp)
print("ROUGE-L: r", rouge_lr)
print("ROUGE-L: f", rouge_lf)