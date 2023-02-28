from flask import Flask, render_template, request
import dill
import pandas as pd
import numpy as np


app = Flask(__name__)

with open('../models/topic_nb_best_cv.pkl', 'rb') as f:
    main_varietal_model = dill.load(f)
    
with open('../models/sentiment_xgb_best_cv.pkl', 'rb') as f:
    sentiment_model = dill.load(f)
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_data = request.form['input_data']
        input_data = [input_data]
        input_data = pd.DataFrame(data = input_data, columns = ['reviewer_text'])
        main_varietal_prediction = main_varietal_model.predict(input_data)
        sentiment_prediction = sentiment_model.predict(input_data)
        return render_template('result.html', 
                               main_varietal = main_varietal_prediction[0], 
                               sentiment = sentiment_prediction[0])
    else:
        return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug = True)