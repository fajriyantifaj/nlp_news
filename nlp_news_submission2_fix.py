# -*- coding: utf-8 -*-
"""nlp_news_submission2_fix.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LUIDrUzzXQ3uyjQx-CY_nGet9QbWcGp_

#**Fajri Yanti** 

> M03 - m314y0826@dicoding.org/20106311700069@student.unsika.ac.id

> Universitas Singaperbangsa Karawang

**train.csv:**

A full training dataset with the following attributes:
*   id: unique id for a news article
*   text: the text of the article; could be incomplete
*   author: author of the news article
*   title: the title of a news article
*   label: a label that marks the article as potentially unreliable
*   1: unreliable
*   0: reliable
"""

# Commented out IPython magic to ensure Python compatibility.
import seaborn as sns
import nltk
import csv
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import warnings
import tensorflow as tf
warnings.filterwarnings('ignore')
from keras.layers import Embedding
from sklearn.model_selection import train_test_split
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences

df = pd.read_csv('train.csv')
df.head()

df['title'][0]

df['text'][0]

df.info()

df = df.drop(columns=['id', 'author', 'title'], axis=1)

df = df.dropna(axis=0)

len(df)

df_news= df['text'].str.lower()
df_news

df_news = df_news.str.replace('\n', ' ')
df_news = df_news.str.replace('[^A-Za-z0-9\s]', '')
df_news = df_news.str.replace('\s+', ' ')

df_news

stop = stopwords.words('english')
df_news = df_news.apply(lambda x: " ".join([word for word in x.split() if word not in stop])) 
df.head()

"""##**Word Tokenization-Embedding**"""

tokenizer = Tokenizer()
tokenizer.fit_on_texts(df_news)
word_index = tokenizer.word_index
vocab_size = len(word_index)
vocab_size

sequences = tokenizer.texts_to_sequences(df_news)
sequence_train = pad_sequences(sequences, maxlen=700, 
                               padding='post', truncating='post')

"""**Embedding Matrix**"""

from keras.layers import Embedding
embedding_index = {}
with open('glove.6B.100d.txt') as f:
  for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embedding_index[word] = coefs

embedding_matrix = np.zeros((vocab_size+1, 100))
for word, i in word_index.items():
    embedding_vector = embedding_index.get(word)
    if embedding_vector is not None:
       embedding_matrix[i] = embedding_vector

embedding_matrix[2]

sequence_train[2]

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(sequence_train, df['label'],
                                                    test_size=0.2, random_state=42,
                                                    stratify=df['label'])

"""##**MODEL TRAINING**"""

from keras.layers import LSTM, Dropout, Dense, Embedding
from  keras import Sequential 

model = Sequential([
    Embedding(vocab_size+1, 100, weights=[embedding_matrix], trainable=False),
    Dropout(0.2),
    LSTM(128, return_sequences=True),
    LSTM(128),
    Dropout(0.2),
    Dense(512),
    Dropout(0.2),
    Dense(256),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy', 
    metrics='accuracy'
)
model.summary()

accuracy_threshold = 98e-2
class cbacks(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs = None):
        if logs.get('accuracy') >= accuracy_threshold:
            print('\nFor Epoch', epoch, 
                  '\nAccuracy has reach = %2.2f%%' %(logs['accuracy']*100),
                  'training has been stopped.')
            self.model.stop_training = True

history = model.fit(x_train, y_train, epochs=14, batch_size=128, 
                    validation_data=[x_test, y_test], callbacks = [cbacks()])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.xlabel('eporchs')
plt.ylabel('accuracy')
plt.legend(['Train', 'Test'])
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.xlabel('eporchs')
plt.ylabel('loss')
plt.legend(['Train', 'Test'])
plt.show()