# -*- coding: utf-8 -*-
"""(Deep_Learning)_Word2Vec_(17_12_2021)_(SEM__ELOC).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LOukoz1qH6_xE8qfkrG0AuqZZi0xN5oq
"""

!gdown --id 1tvoH7zg0WNjvIJPK85NSGVEm9D7Xvhs6
!gdown --id 16Q-ncigrNzFKMXsdZS9F2n8N9okWHBUB
!gdown --id 1cJe2pmeAzD_KPHxdeQBmGfxEJfcuUSTr

import nltk
nltk.download(["wordnet","punkt"])

import re
import matplotlib.pyplot as plt
import string
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
from collections import Counter
from nltk.corpus import stopwords
import nltk
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

"""# Data importing"""

df = pd.read_csv(r"SEM-EL-OC DATASET.csv")

"""# Data exploration"""

df.head(5)

len(df)

df['label'].unique()

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
    # if labels[i] == 'surprise':
    #     y.append(4)
    # if labels[i] == 'disgust':
    #     y.append(5)
    # if labels[i] == 'trust':
    #     y.append(6)
    # if labels[i] == 'anticipation':
    #     y.append(7)

y = np.array(y)
labels = tf.keras.utils.to_categorical(y, 4, dtype="float32")
del y

"""# Data sequencing and splitting

"""

clean_tweet_stemmed = df['clean_tweet_stemmed'].values.astype('U')

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
max_words = 2000 
max_len = 200 

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(df["clean_tweet_no_stop"])
sequences = tokenizer.texts_to_sequences(df["clean_tweet_no_stop"])
tweets = pad_sequences(sequences, maxlen=max_len) 
print(tweets)

"""###AraVec 2.0 (Twitter-CBOW)"""

import gensim
word_index = tokenizer.word_index 
EMBEDDING_DIM = 300 
embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))

#load the gensim embedding model  
model = gensim.models.Word2Vec.load('tweets_cbow_300') 
import re

#this function is provided by the author from the AraVec 2.0 (Twitter-CBOW), it preprocess the data. 
def clean_str(text):
    search = ["أ","إ","آ","ة","_","-","/",".","،"," و "," يا ",'"',"ـ","'","ى","\\",'\n', '\t','&quot;','?','؟','!']
    replace = ["ا","ا","ا","ه"," "," ","","",""," و"," يا","","","","ي","",' ', ' ',' ',' ? ',' ؟ ',' ! ']
    
    #remove tashkeel
    p_tashkeel = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    text = re.sub(p_tashkeel,"", text)
    
    #remove longation
    p_longation = re.compile(r'(.)\1+')
    subst = r"\1\1"
    text = re.sub(p_longation, subst, text)
    
    text = text.replace('وو', 'و')
    text = text.replace('يي', 'ي')
    text = text.replace('اا', 'ا')
    
    for i in range(0, len(search)):
        text = text.replace(search[i], replace[i])
    
    #trim    
    text = text.strip()

    return text
  
#here we are creating a embedding matrix with embedding vector assigned to each word.
unassigned = []
for word, i in word_index.items():
    word_c = clean_str(word)
    try:
       embedding_vector =  model.wv[ word_c ]
    except:
      embedding_vector = np.zeros(EMBEDDING_DIM)
      unassigned.append(i)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector
print("unassigned words", len(unassigned))

# Randomly shuffling data
from sklearn.utils import shuffle
df = shuffle(df)
df.head(5)

tweets.shape

print(labels)

#Splitting the data
X_train, X_test, y_train, y_test = train_test_split(tweets,labels, test_size=0.3, random_state=42, stratify=labels)
print (len(X_train),len(X_test),len(y_train),len(y_test))

"""# Model building

## Single LSTM layer model
"""

model1 = Sequential()
# adding layer

# here is embedding layer supporting for both pretrained models. 
model1.add(layers.Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=max_len,
                            trainable=False))

# Adding LSTM layer
model1.add(layers.LSTM(128,dropout=0.1))

# Adding dense layer with softmax activation
model1.add(layers.Dense(4,activation='softmax'))

optimizer = tf.keras.optimizers.Adam(lr=0.002)

model1.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

#Implementing model checkpoins to save the best metric and do not lose it on training.
checkpoint1 = ModelCheckpoint("best_model1.hdf5", monitor='val_accuracy', verbose=1,save_best_only=True, mode='auto', period=1,save_weights_only=False)
history = model1.fit(X_train, y_train, epochs=15, batch_size=16, validation_data=(X_test, y_test),callbacks=[checkpoint1])

best_model1 = keras.models.load_model("best_model1.hdf5")
test_loss, test_acc = best_model1.evaluate(X_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model1.predict(X_test)
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print(classification_report(np.argmax(y_test, axis=1), np.argmax(predictions, axis=1)))

"""## Bidirectional LTSM model"""

# Model
model2 = Sequential()
model2.add(layers.Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=max_len,
                            trainable=False))

# Adding bidirectional LSTM layer
model2.add(layers.Bidirectional(layers.LSTM(128,dropout=0.1)))

# Adding dense layer with softmax activation
model2.add(layers.Dense(4,activation='softmax'))
optimizer = tf.keras.optimizers.Adam(lr=0.002)

model2.compile(optimizer=optimizer,loss='categorical_crossentropy', metrics=['accuracy'])

#Implementing model checkpoins to save the best metric and do not lose it on training.
checkpoint2 = ModelCheckpoint("best_model2.hdf5", monitor='val_accuracy', verbose=1,save_best_only=True, mode='auto', period=1,save_weights_only=False)

history = model2.fit(X_train, y_train, epochs=15,batch_size= 16, validation_data=(X_test, y_test),callbacks=[checkpoint2])

best_model2 = keras.models.load_model("best_model2.hdf5")
test_loss, test_acc = best_model2.evaluate(X_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model2.predict(X_test)
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print(classification_report(np.argmax(y_test, axis=1), np.argmax(predictions, axis=1)))

"""## 1D Convolutional model"""

from keras import regularizers
model3 = Sequential()
model3.add(layers.Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=max_len,
                            trainable=False))
model3.add(layers.Conv1D(100, 6, activation='relu',kernel_regularizer=regularizers.l1_l2(l1=2e-3, l2=2e-3),bias_regularizer=regularizers.l2(2e-3)))
model3.add(layers.MaxPooling1D(5))
model3.add(layers.Conv1D(100, 6, activation='relu',kernel_regularizer=regularizers.l1_l2(l1=2e-3, l2=2e-3),bias_regularizer=regularizers.l2(2e-3)))
model3.add(layers.GlobalMaxPooling1D())
model3.add(layers.Dense(4,activation='softmax'))

optimizer = tf.keras.optimizers.RMSprop(
     learning_rate=0.002,
     rho=0.9,
     momentum=0.0,
     epsilon=1e-07,
     centered=False,
     name="RMSprop")

model3.compile(optimizer=optimizer, loss='categorical_crossentropy',metrics=['accuracy'])
checkpoint3 = ModelCheckpoint("best_model3.hdf5", monitor='val_accuracy', verbose=1,save_best_only=True, mode='auto', period=1,save_weights_only=False)
history = model3.fit(X_train, y_train, epochs=20, batch_size= 8, validation_data=(X_test, y_test),callbacks=[checkpoint3])

best_model3 = keras.models.load_model("best_model3.hdf5")
test_loss, test_acc = best_model3.evaluate(X_test, y_test, verbose=2)
print('Model accuracy: ',test_acc)

predictions = best_model3.predict(X_test)
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print(classification_report(np.argmax(y_test, axis=1), np.argmax(predictions, axis=1)))