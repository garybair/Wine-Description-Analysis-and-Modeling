from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form['text']
        prediction = predict(text)
        return render_template('result.html', prediction=prediction)
    return render_template('index.html')
    
    
if __name__ == '__main__':
    app.run(debug=True)
    
<!DOCTYPE html>
<html>
  <head>
    <title>My Flask App</title>
  </head>
  <body>
    <form method="POST" action="/">
      <input type="text" name="text">
      <button type="submit">Submit</button>
    </form>
  </body>
</html>