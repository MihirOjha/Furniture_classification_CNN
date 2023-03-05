import os
import uuid
import urllib.request
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request
from markupsafe import escape

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'image_classifier.h5'))
ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXT

class_labels = ['Bed', 'Chair', 'Sofa']

def predict(filename, model):
    img = Image.open(filename)
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = img_array.astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    preds = model.predict(img_array)[0]
    results = {class_labels[i]: float(preds[i]) for i in range(len(class_labels))}
    return results,filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_image():
    error = ''
    if 'file' not in request.files and 'link' not in request.form:
        error = 'Image file or link not included in request'
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            error = 'No selected file'
        elif file and allowed_file(file.filename):
            unique_filename = str(uuid.uuid4())
            filename = unique_filename + ".jpg"
            img_path = os.path.join('static/images', filename)
            file.save(img_path)
            results, img_path = predict(img_path, model)
        else:
            error = 'Please upload images of jpg, jpeg, png, and jfif extension only'
    elif 'link' in request.form:
        link = request.form['link']
        try:
            resource = urllib.request.urlopen(link)
            unique_filename = str(uuid.uuid4())
            filename = unique_filename + ".jpg"
            img_path = os.path.join('static/images', filename)
            output = open(img_path, "wb")
            output.write(resource.read())
            output.close()
            results, img_path = predict(img_path, model)
        except Exception as e:
            error = 'This image from this site is not accessible or inappropriate input'

    if error:
        return render_template('index.html', error=error)
    else:
        return render_template('results.html', results=results, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)

