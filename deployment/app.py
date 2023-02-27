from flask import Flask, render_template, request, jsonify
import dill
import os
import sys
sys.path.append('../src/')

app = Flask(__name__)

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
models_folder = parent_directory + '/src/'

#with open(models_folder + 'sia_pipeline.pkl', 'rb') as f:
#    sentiment_model = dill.load(f)
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_data = request.form['input_data']
        main_varietal_prediction = main_varietal_model.predict([input_data])[0]
        sub_varietal_prediction = sub_varietal_model.predict([input_data])[0]
        sentiment_prediction = sentiment_model.predict([input_data])[0]
        return render_template('result.html', 
                               main_varietal = main_varietal_prediction, 
                               sub_varietal = sub_varietal_prediction,
                               sentiment = sentiment_prediction,)
    else:
        return render_template('landing_form.html')
    
    
if __name__ == '__main__':
    app.run(debug=True)