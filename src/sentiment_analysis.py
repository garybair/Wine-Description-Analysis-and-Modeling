import pandas as pd
import numpy as np
import re
import nltk

# pipeline tools
from sklearn.base import TransformerMixin

#models
from nltk.sentiment import SentimentIntensityAnalyzer

class SIATransformer(TransformerMixin):
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.sia_transformer_lambda = lambda x: self.sia.polarity_scores(x)['compound']
        
    def transform(self, X):
        return np.vectorize(self.sia_transformer_lambda)(X)

    def fit(self, X, y=None):
        return self
    
class SIAScaler(TransformerMixin):
    def __init__(self):
        self.sia_scaler_lambda = lambda x: (x - (-1))*100/(2)
    
    def transform(self, X):
        return np.vectorize(self.sia_scaler_lambda)(X)

    def fit(self, X, y=None):
        return self
    
    def predict(self, X):
        return np.vectorize(self.sia_scaler_lambda)(X)
    
class CovertToList(TransformerMixin):
    def transform(self, X):
        transformed_data = []
        #transform to dataframe
        X = pd.DataFrame(X)
        #get colnames
        colnames = X.columns
        #iterate through columns
        for col in colnames:
            X = X[col].tolist()
            X = [str(i) for i in X]
            transformed_data.extend(X)
        return np.array(transformed_data)

    def fit(self, X, y=None):
        return self