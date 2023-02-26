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
        if isinstance(X, pd.Series):
            #standardize type
            X = X.astype(str)
            # lower text
            X = X.str.lower()
            # remove punctuation
            X = X.str.replace('\W+', ' ', regex = True)
            # tokenize text into individual words
            X = X.str.split()
            # remove stopwords
            X = X.apply(lambda x: [word for word in x if word not in (self.stop_words)])
            # join words
            X = X.apply(lambda x: ' '.join(x))
            return X
        elif isinstance(X, pd.DataFrame):
            colnames = X.columns
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
            return X
        else:
            return X
    
    def fit(self, X, y=None):
        return self