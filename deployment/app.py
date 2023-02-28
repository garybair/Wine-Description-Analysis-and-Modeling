from flask import Flask, render_template, request, jsonify
import dill
import os
import sys
sys.path.append('../src')
import preprocessing
import pandas as pd
import numpy as np
import traceback

app = Flask(__name__)

with open('../models/topic_nb_best_cv.pkl', 'rb') as f:
    main_varietal_model = dill.load(f)
    
with open('../models/sentiment_xgb_best_cv.pkl', 'rb') as f:
    sentiment_model = dill.load(f)
    
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            input_data = request.form['input_data']
            input_data = [input_data]
            input_data = pd.DataFrame(data = input_data, columns = ['reviewer_text'])
            main_varietal_prediction = main_varietal_model.predict(input_data)
            sentiment_prediction = sentiment_model.predict(input_data)
            return render_template('result.html', 
                                   main_varietal = str(main_varietal_prediction), 
                                   sentiment = str(sentiment_prediction))
        else:
            return render_template('landing_form.html')

    except Exception:
        traceback.print_exc()
    
if __name__ == '__main__':
    app.run()
    