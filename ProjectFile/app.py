import os
from flask import Flask, render_template, request, url_for, redirect, session
from openai import OpenAI
from cleanData import cleanData
from askGPT import askGPT

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'data/unsortedData'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.secret_key = os.urandom(24)

@app.route("/", methods=['GET', 'POST'])
def index():
    GptOutput = None
    fromDate = None
    toDate = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'date_form':
            fromDate = request.form['from']
            toDate = request.form['to']
            session['fromDate'] = fromDate
            session['toDate'] = toDate
            print(fromDate, toDate)
        elif form_type == 'query_form' and 'fromDate' in session and 'toDate' in session:
            question = request.form['queryelement']
            fromDate = session['fromDate']
            toDate = session['toDate']
            GptOutput = askGPT(question, fromDate, toDate)
            session.pop('fromDate', None)
            session.pop('toDate', None)
        return redirect(url_for('index'))

    fromDate = session.get('fromDate')
    toDate = session.get('toDate')
    return render_template('index.html', GptOutput=GptOutput, fromDate=fromDate, toDate=toDate)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file = None
    if request.method == 'POST':
        file = request.files['files']
        month = request.form['month']
        filename = f"{month}.csv"
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