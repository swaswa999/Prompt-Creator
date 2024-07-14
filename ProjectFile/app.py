import os
from flask import Flask, render_template, request, url_for, redirect
from openai import OpenAI
from cleanData import cleanData

app = Flask(__name__)

GptOutput = None
file = None
app.config['UPLOAD_FOLDER'] = 'data/unsortedData'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form['queryelement']
    if GptOutput != None:
        return render_template('index.html', GptOutput=GptOutput)
    else:
        return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file = None
    if request.method == 'POST':
        file = request.files['files']
        filename = request.form['month']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cleanData(filename)

    if file != None:
        return redirect('/')
    else:
        return render_template('upload.html')

@app.route('/uploaded')
def uploaded():
    return render_template('uploaded.html')




if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 81))
    app.run(host=host, port=port, debug=True)