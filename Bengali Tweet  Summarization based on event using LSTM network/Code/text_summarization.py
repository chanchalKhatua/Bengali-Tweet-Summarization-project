#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import string
from string import digits
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import re
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from keras.layers import Input, LSTM, Embedding, Dense
from keras.models import Model

#imported the datasets
lines=pd.read_csv("/content/databasecsvnew12 - Sheet1.csv")

# Remove quotes
lines.orginalText=lines.orginalText.apply(lambda x: re.sub("'", '', x))
lines.summaryText=lines.summaryText.apply(lambda x: re.sub("'", '', x))
# Remove quotes
lines.orginalText=lines.orginalText.apply(lambda x: re.sub(r"\r", "", x))
lines.summaryText=lines.summaryText.apply(lambda x: re.sub(r"\r", "", x))
exclude = set(string.punctuation) # Set of all special characters
# Remove all the special characters
lines.orginalText=lines.orginalText.apply(lambda x: ''.join(ch for ch in x if ch not in exclude))
lines.summaryText=lines.summaryText.apply(lambda x: ''.join(ch for ch in x if ch not in exclude))
# Remove extra spaces
lines.orginalText=lines.orginalText.apply(lambda x: x.strip())
lines.summaryText=lines.summaryText.apply(lambda x: x.strip())
lines.orginalText=lines.orginalText.apply(lambda x: re.sub(" +", " ", x))
lines.summaryText=lines.summaryText.apply(lambda x: re.sub(" +", " ", x))
lines.summaryText = lines.summaryText.apply(lambda x : 'START_ '+ x + ' _END')
lines.sample(10)


# Vocabulary of orginaltext
all_orginal_words=set()
for orginal in lines.orginalText:
    for word in orginal.split():
        if word not in all_orginal_words:
            all_orginal_words.add(word)

# Vocabulary of summary
all_summary_words=set()
for summary in lines.summaryText:
    for word in summary.split():
        if word not in all_summary_words:
            all_summary_words.add(word)
lines.orginalText[1]            

# Max Length of target sequence
lenght_list=[]
for l in lines.summaryText:
    lenght_list.append(len(l.split(' ')))
max_length_tar = np.max(lenght_list)
max_length_tar+1
input_words = sorted(list(all_orginal_words))
target_words = sorted(list(all_summary_words))
num_encoder_tokens = len(all_orginal_words)
num_decoder_tokens = len(all_summary_words)
num_decoder_tokens += 1 # For zero padding
print(max_length_tar)
print(num_decoder_tokens)
print(num_encoder_tokens)

#map words to unique integer indices for both input and target words
input_token_index = dict([(word, i+1) for i, word in enumerate(input_words)])
target_token_index = dict([(word, i+1) for i, word in enumerate(target_words)])

# map integer indices back to their original words
reverse_input_char_index = dict((i, word) for word, i in input_token_index.items())
reverse_target_char_index = dict((i, word) for word, i in target_token_index.items())

lines = shuffle(lines)
lines.head(10)


# In[ ]:


# Train - Test Split
X, y = lines.orginalText, lines.summaryText
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.1)
X_train.shape, X_test.shape


# In[ ]:


#loading complex data structures without losing their internal structure or format
X_train.to_pickle('X_train.pkl')
X_test.to_pickle('X_test.pkl')


# In[ ]:


def generate_batch(X = X_train, y = y_train, batch_size = 128):
    ''' Generate a batch of data '''
    while True:
        for j in range(0, len(X), batch_size):
            encoder_input_data = np.zeros((batch_size, max_length_src),dtype='float32')
            decoder_input_data = np.zeros((batch_size, max_length_tar),dtype='float32')
            decoder_target_data = np.zeros((batch_size, max_length_tar, num_decoder_tokens),dtype='float32')
            for i, (input_text, target_text) in enumerate(zip(X[j:j+batch_size], y[j:j+batch_size])):
                for t, word in enumerate(input_text.split()):
                    encoder_input_data[i, t] = input_token_index[word] # encoder input seq
                for t, word in enumerate(target_text.split()):
                    if t<len(target_text.split())-1:
                        decoder_input_data[i, t] = target_token_index[word] # decoder input seq
                    if t>0:
                        # decoder target sequence (one hot encoded)
                        # does not include the START_ token
                        # Offset by one timestep
                        decoder_target_data[i, t - 1, target_token_index[word]] = 1.
            yield([encoder_input_data, decoder_input_data], decoder_target_data)


# In[ ]:


latent_dim = 100


# In[ ]:


# Encoder
encoder_inputs = Input(shape=(None,))
enc_emb =  Embedding(num_encoder_tokens, latent_dim, mask_zero = True)(encoder_inputs)
encoder_lstm = LSTM(latent_dim, return_state=True)
encoder_outputs, state_h, state_c = encoder_lstm(enc_emb)
# We discard `encoder_outputs` and only keep the states.
encoder_states = [state_h, state_c]


# In[ ]:


# Set up the decoder, using `encoder_states` as initial state.
decoder_inputs = Input(shape=(None,))
dec_emb_layer = Embedding(num_decoder_tokens, latent_dim, mask_zero = True)
dec_emb = dec_emb_layer(decoder_inputs)
# We set up our decoder to return full output sequences,
# and to return internal states as well. We don't use the
# return states in the training model, but we will use them in inference.
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(dec_emb,
                                     initial_state=encoder_states)
decoder_dense = Dense(num_decoder_tokens, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Define the model that will turn
# `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)


# In[ ]:


model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['acc'])


# In[ ]:


history=model.fit_generator(generator = generate_batch(X_train, y_train, batch_size = batch_size),
                    steps_per_epoch = train_samples//batch_size,
                    epochs=epochs,
                    validation_data = generate_batch(X_test, y_test, batch_size = batch_size),
                    validation_steps = val_samples//batch_size)


# In[ ]:


# Encode the input sequence to get the "thought vectors"
encoder_model = Model(encoder_inputs, encoder_states)

# Decoder setup
# Below tensors will hold the states of the previous time step
decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

dec_emb2= dec_emb_layer(decoder_inputs) # Get the embeddings of the decoder sequence

# To predict the next word in the sequence, set the initial states to the states from the previous time step
decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb2, initial_state=decoder_states_inputs)
decoder_states2 = [state_h2, state_c2]
decoder_outputs2 = decoder_dense(decoder_outputs2) # A dense softmax layer to generate prob dist. over the target vocabulary

# Final decoder model
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs,
    [decoder_outputs2] + decoder_states2)


# In[ ]:


def decode_sequence(input_seq):
    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)
    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1,1))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0] = target_token_index['START_']

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size 1).
    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict([target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += ' '+sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '_END' or
           len(decoded_sentence) > 150):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1,1))
        target_seq[0, 0] = sampled_token_index

        # Update states
        states_value = [h, c]

    return decoded_sentence


# In[ ]:


train_gen = generate_batch(X_train, y_train, batch_size = 1)
k=-1


# In[ ]:


k+=1
(input_seq, actual_output), _ = next(train_gen)
decoded_sentence = decode_sequence(input_seq)
print('Input seuence:', X_train[k:k+1].values[0])
print('Actual summary:', y_train[k:k+1].values[0][6:-4])
print('Predicted summary:', decoded_sentence[:-4])

