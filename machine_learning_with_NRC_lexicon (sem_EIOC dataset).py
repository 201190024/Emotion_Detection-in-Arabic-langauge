# -*- coding: utf-8 -*-
"""Machine_Learning_with_NRC_Lexicon_Results_(SEM_ELOC)(12_8_2021).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BFQQnFXvwAhEWHOQC8FLmSJTt2Sy2Y-N
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd
import numpy as np
import nltk
import future
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import re
from sklearn import metrics

df = pd.read_csv(r"feature extraction with NRC(SEM-EL-OC DATASET).csv")
df.head(5)

len(df)

from sklearn.utils import shuffle
df = shuffle(df)
df = shuffle(df)
df = shuffle(df)
df.head(5)

x = df['clean_tweet_stemmed'].values.astype('U')
x_enc = x
y_enc = df[['label']].values#encode(le, y)
x_enc.shape
y_enc.shape

vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w\w+\b")
x_tfidf = vectorizer.fit_transform(x_enc)
x_tfidf.shape

tf_features = x_tfidf.toarray()
tf_features.shape

other_features = df[["lexicon_score_anger","lexicon_score_fear","lexicon_score_joy", "lexicon_score_sadness"]].values
other_features.shape

import numpy as np
x_tfidf = np.concatenate((tf_features, other_features), axis=1)
x_tfidf.shape

x_train, x_test, y_train, y_test = train_test_split(x_tfidf, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

x_train.shape

x_test.shape

y_train.shape

y_test.shape

def modelEvaluation(predictions, y_test_set):
    print("\nAccuracy on validation set: {:.4f}".format(accuracy_score(y_test_set, predictions)))
    print("\nClassification report : \n", metrics.classification_report(y_test_set, predictions))
    print("\nConfusion Matrix : \n", metrics.confusion_matrix(y_test_set, predictions))

mnb = MultinomialNB(alpha=0.2)
mnb.fit(x_train, y_train)

predictions = mnb.predict(x_test)
modelEvaluation(predictions, y_test)

svr_lin = svm.LinearSVC()
svr_lin.fit(x_train, y_train)
y_svr_lin_predicted = svr_lin.predict(x_test)
modelEvaluation(y_svr_lin_predicted, y_test)

#Logistic Regression
lr = LogisticRegression()
lr.fit(x_train, y_train)
# Evaluate on the validaton set

predictions = lr.predict(x_test)
modelEvaluation(predictions, y_test)

mlp = MLPClassifier(hidden_layer_sizes=(100), activation='relu', solver='adam', alpha=0.01, batch_size='auto', learning_rate='constant')
mlp.fit(x_train, y_train)
#Evaluate on the validaton set
predictions = mlp.predict(x_test)
modelEvaluation(predictions, y_test)

