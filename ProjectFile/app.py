import os
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
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
        fromDate = request.form['fromHidden']
        toDate = request.form['toHidden']
        userQuestion = request.form['queryelement']
        GptOutput = askGPT(userQuestion, fromDate, toDate)

    return render_template('index.html', GptOutput=GptOutput, fromDate=fromDate, toDate=toDate)

@app.route("/fetch_data", methods=['GET'])
def fetch_data():
    fromDate = request.args.get('from')
    toDate = request.args.get('to')
    # Fetch your data based on fromDate and toDate
    pieChart = [200, 200, 150, 175, 125, 300, 250, 275, 225]
    expenseTrend = [90, 180, 140, 160, 120, 280, 230, 260, 210]
    CostTrack = [110, 220, 160, 190, 130, 320, 270, 290, 240]
    data = {
        "pieChart": pieChart,
        "expenseTrend": expenseTrend,
        "CostTrack": CostTrack
    }
    return jsonify(data)

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
    csvFileList = []
    unsortedList = sorted(os.listdir('data/'))
    for n in range(len(unsortedList)):
        if unsortedList[n].endswith('.csv'):
            csvFileList.append(unsortedList[n])
    return render_template('uploaded.html', csvFileList=csvFileList)

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 81))
    app.run(host=host, port=port, debug=True)
