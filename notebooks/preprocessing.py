#imports
import numpy as np
import pandas as pd
import re
import string
from sklearn.base import TransformerMixin
from nltk.corpus import stopwords

class preprocess_text(TransformerMixin):
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def transform(self, X):
        #transform to dataframe
        X = pd.DataFrame(X)
        #get colnames
        colnames = X.columns
        #iterate through columns
        for col in colnames:
            #standardize type
            X[col] = X[col].astype(str)
            # convert text to lowercase
            X[col] = X[col].str.lower()
            # remove punctuation
            X[col] = X[col].str.replace('\W+', ' ', regex = True)
            # tokenize text into individual words
            X[col] = X[col].str.split()
            # remove stopwords
            X[col] = X[col].apply(lambda x: [word for word in x if word not in (self.stop_words)])
            # join words
            X[col] = X[col].apply(lambda x: ' '.join(x))
        #write to array
        X = X.values
        return X
    
    def fit(self, X, y=None):
        return self