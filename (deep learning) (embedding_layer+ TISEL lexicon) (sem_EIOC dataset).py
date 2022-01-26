# -*- coding: utf-8 -*-
"""DL_(Embedding_layer_+_lexicon_(SEL)_22_1_2022)_(SEM_ELOC).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1arrVnnjZW2kjQyEbbqgR93wb2ovxKvNc

# Imports
"""

import re
import matplotlib.pyplot as plt
import string
from nltk.corpus import stopwords
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
from collections import Counter
from nltk.corpus import stopwords
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
import spacy
import pickle
import warnings
warnings.filterwarnings('ignore')
import seaborn as sns
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt 
import tensorflow as tf
import keras
import numpy as np
import pandas as pd
print('Done')

"""# Data importing with NRC Lexicon Features

# Reading Data
"""

df = pd.read_csv(r"feature extraction with SEL (SEM-ELOC).csv")
df.head(5)

df.shape

df['label'].unique()

clean_tweet_stemmed = df['clean_tweet_stemmed'].values.astype('U')

labels = np.array(df['label'])
y = []
for i in range(len(df["label"])):
    if labels[i] == 'anger':
        y.append(0)
    if labels[i] == 'sadness':
        y.append(1)
    if labels[i] == 'fear':
        y.append(2)
    if labels[i] == 'joy':
        y.append(3)
 


y = np.array(y)
labels = tf.keras.utils.to_categorical(y, 4, dtype="float32")
del y

"""# Data sequencing and splitting

"""

from keras.models import Sequential
from keras import layers
# from keras.optimizers import RMSprop,Adam
from tensorflow.keras.optimizers import RMSprop
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras import regularizers
from keras import backend as K
from keras.callbacks import ModelCheckpoint

# Number of words in tokens vector
max_words = 5000
max_len = 200


tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(clean_tweet_stemmed)
sequences = tokenizer.texts_to_sequences(clean_tweet_stemmed)
tweets = pad_sequences(sequences, maxlen=max_len)
print(tweets)

tweets_feature = pd.DataFrame(tweets)
tweets_feature.shape

print(labels)

"""# Append NRC Lexicon features"""

df['lexicon_score_anger']  = (df['lexicon_score_anger'] - df['lexicon_score_anger'].min()) /(df['lexicon_score_anger'].max()-df['lexicon_score_anger'].min()) 
df['lexicon_score_fear']  = (df['lexicon_score_fear'] - df['lexicon_score_fear'].min()) /(df['lexicon_score_fear'].max()-df['lexicon_score_fear'].min()) 
df['lexicon_score_joy']  = (df['lexicon_score_joy'] - df['lexicon_score_joy'].min()) /(df['lexicon_score_joy'].max()-df['lexicon_score_joy'].min()) 
df['lexicon_score_sadness']  = (df['lexicon_score_sadness'] - df['lexicon_score_sadness'].min()) /(df['lexicon_score_sadness'].max()-df['lexicon_score_sadness'].min())
# df['lexicon_score_disgust']  = (df['lexicon_score_disgust'] - df['lexicon_score_disgust'].min()) /(df['lexicon_score_disgust'].max()-df['lexicon_score_disgust'].min())
# df['lexicon_score_trust']  = (df['lexicon_score_trust'] - df['lexicon_score_trust'].min()) /(df['lexicon_score_trust'].max()-df['lexicon_score_trust'].min())
# df['lexicon_score_surprise']  = (df['lexicon_score_surprise'] - df['lexicon_score_surprise'].min()) /(df['lexicon_score_surprise'].max()-df['lexicon_score_surprise'].min())
# df['lexicon_score_anticipation']  = (df['lexicon_score_anticipation'] - df['lexicon_score_anticipation'].min()) /(df['lexicon_score_anticipation'].max()-df['lexicon_score_anticipation'].min())

other_featuresNRC = df[["lexicon_score_anger","lexicon_score_fear","lexicon_score_joy", "lexicon_score_sadness"]].values
#  "lexicon_score_disgust", "lexicon_score_trust", "lexicon_score_surprise", "lexicon_score_anticipation"  ]].values
other_featuresNRC.shape

import numpy as np
all_feature = np.concatenate((tweets_feature, other_featuresNRC), axis=1)
# as we see, the the number of features are increase +4, because we concatenate the 4 features from NRC lexicon to the featreus from embedding layer,
# and we will use it in training the models
all_feature.shape

"""##Splitting the data

"""

x_train, x_test, y_train, y_test = train_test_split(all_feature,labels, test_size=0.3, random_state=42, stratify= labels)
print (len(x_train),len(x_test),len(y_train),len(y_test))

"""# Model building

## Single LSTM layer model
"""

model1 = Sequential()
model1.add(layers.Embedding(max_words, 128, input_length=max_len+4))
# model1.add(layers.Embedding(max_words, 20))
model1.add(layers.LSTM(128,dropout=0.5, return_sequences= True))
model1.add(layers.LSTM(64,dropout=0.5, return_sequences= True))
model1.add(layers.LSTM(64,dropout=0.5))
# model1.add(layers.LSTM(32,dropout=0.2, return_sequences= True))
# model1.add(layers.LSTM(16,dropout=0.2)) 
# optimizer = tf.keras.optimizers.Adam(lr=0.002)
optimizer = tf.keras.optimizers.RMSprop(
     learning_rate=0.001,
     rho=0.9,
     momentum=0.0,
     epsilon=1e-07,
     centered=False,
     name="RMSprop")

model1.add(layers.Dense(4,activation='softmax'))
model1.compile(optimizer= optimizer,loss='categorical_crossentropy', metrics=['accuracy'])

#Implementing model checkpoins to save the best metric and do not lose it on training.
checkpoint1 = ModelCheckpoint("best_model1.hdf5", monitor='val_accuracy', verbose=1,save_best_only=True, mode='auto', period=1,save_weights_only=False)
history = model1.fit(x_train, y_train, epochs=15, batch_size = 8, validation_data=(x_test, y_test),callbacks=[checkpoint1])

best_model1 = keras.models.load_model("best_model1.hdf5")
test_loss, test_acc = best_model1.evaluate(x_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model1.predict(x_test)
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print(classification_report(np.argmax(y_test, axis=1), np.argmax(predictions, axis=1)))

"""## Bidirectional LTSM model"""

model2 = Sequential()
# max_len+8 --- 8 here means that we have now additional eight features - ie lexicons -anger, fear, sadness, joy
model2.add(layers.Embedding(max_words, 128, input_length=max_len+4))
model2.add(layers.Bidirectional(layers.LSTM(64,dropout=0.5)))
model2.add(layers.Dense(4,activation='softmax'))
# optimizer = tf.keras.optimizers.Adam(lr=0.002)
optimizer = tf.keras.optimizers.RMSprop(
     learning_rate=0.002,
     rho=0.9,
     momentum=0.0,
     epsilon=1e-07,
     centered=False,
     name="RMSprop")

model2.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
#Implementing model checkpoins to save the best metric and do not lose it on training.
checkpoint2 = ModelCheckpoint("best_model2.hdf5", monitor='val_accuracy', verbose=1,save_best_only=True, mode='auto', period=1,save_weights_only=False)
history = model2.fit(x_train, y_train, epochs=10, batch_size= 32, validation_data=(x_test, y_test),callbacks=[checkpoint2])

best_model2 = keras.models.load_model("best_model2.hdf5")
test_loss, test_acc = best_model2.evaluate(x_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model2.predict(x_test)
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print(classification_report(np.argmax(y_test, axis=1), np.argmax(predictions, axis=1)))

"""#CNN MODEL"""

from keras import regularizers
model4 = Sequential()

model4.add(layers.Embedding(max_words, 40, input_length=max_len+4))

model4.add(layers.Conv1D(128, 6, activation='relu'))
model4.add(layers.MaxPooling1D(5))
model4.add(layers.Conv1D(64, 6, activation='relu'))

model4.add(layers.GlobalMaxPooling1D())

model4.add(layers.Dense(4,activation='softmax'))

optimizer = tf.keras.optimizers.RMSprop(
     learning_rate=0.001,
     rho=0.9,
     momentum=0.0,
     epsilon=1e-07,
     centered=False,
     name="RMSprop")

model4.compile(optimizer=optimizer,loss='categorical_crossentropy',metrics=['accuracy'])
checkpoint4 = ModelCheckpoint("best_model4.hdf5", monitor='val_accuracy', verbose=1,save_best_only=True, mode='auto', period=1,save_weights_only=False)
history = model4.fit(x_train, y_train, epochs=20, batch_size= 8,validation_data=(x_test, y_test), callbacks=[checkpoint4])

best_model4 = keras.models.load_model("best_model4.hdf5")
test_loss, test_acc = best_model4.evaluate(x_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model4.predict(x_test)
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print(classification_report(np.argmax(y_test, axis=1), np.argmax(predictions, axis=1)))

