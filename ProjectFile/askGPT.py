import os
import pandas as pd
from datetime import datetime
from openai import OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def addToConvo(question, fromDate, toDate, generated_text):
    f = open("ProjectFile/tempConvoHistory.txt", "a")
    f.write(f"{question}___{fromDate}___{toDate}___{generated_text}\n")
    f.close()
def clearConvo():
    open('ProjectFile/tempConvoHistory.txt', 'w').close()
def accessConvo():
    f = open("ProjectFile/tempConvoHistory.txt", "r")
    convo = f.read()
    return convo

def cleanListRange(fromDate, toDate, unflilterd_dir_list):
    start = datetime.strptime(fromDate, "%Y-%m")
    end = datetime.strptime(toDate, "%Y-%m")
    all_months = []
    current = start
    while current <= end:
        all_months.append(current.strftime("%Y-%m"))
        next_month = current.month % 12 + 1
        next_year = current.year + (current.month // 12)
        current = datetime(next_year, next_month, 1)
    filtered_months = [month for month in all_months if month in unflilterd_dir_list]
    if fromDate not in filtered_months:
        filtered_months.insert(0, fromDate)
    if toDate not in filtered_months:
        filtered_months.append(toDate)

    result = [f"{month}.csv" for month in filtered_months]
    return result

def cvsToString(fileName):
    df = pd.read_csv(f'data/{fileName}')
    data_str = df.to_string()
    return data_str

def allData(fromDate, toDate):
    fileName = None
    unflilterd_dir_list = []
    unflilterd_list = []
    dir_list = []
    dataString = {}
    unsortedList = os.listdir('data/')
    for n in range(len(unsortedList)):
        if unsortedList[n].endswith('.csv'):
            unflilterd_list.append(unsortedList[n])

    unflilterd_dir_list = [fFile[:-4] for fFile in unflilterd_list]

    dir_list = cleanListRange(fromDate, toDate, unflilterd_dir_list)
    for i in range(len(dir_list)):
        fileName = dir_list[i]
        try:
            dataString[fileName] = cvsToString(fileName)
        except:
            print("")
    return dataString

def askGPT(question, fromDate, toDate):
    data = allData(fromDate, toDate)
    client = OpenAI(api_key=OPENAI_API_KEY)
    pastConvo = accessConvo()
    if data != None and question.lower()!= 'clear':
        try:
            client = client.chat.completions.create(model="gpt-4o-mini",
                messages=[
                {"role": "system", "content":f'''High Level Accountant  and a financial advisor,
                    ChatGPT, you are a high-level accountant and financial advisor. Your task is to analyze the provided data, answer the questions, and offer professional suggestions. Follow these steps to ensure thorough and accurate responses:

                    Data Analysis:
                        Carefully examine the data provided within the ``` marks.
                        Identify key financial metrics, trends, and insights relevant to the question.
                    Question Response:
                        Answer the question clearly and concisely based on the analyzed data.
                        Support your answer with specific references to the data.
                    Professional Suggestions:
                        Offer well-considered financial advice or recommendations.
                        Consider potential implications and alternatives for each suggestion.
                    Question: {question}
                    Past Convo: ~~~{pastConvo}~~~
                        You may be givin a past convo history, if you see nothing incased in the ~~~'s than ignore this line
                    Output:
                        The output of your responce should be clean, easy to understand and as short and to the point as possible.
                        The output should not be a tutorial but rather concrete answer, for example if the user askes by what % did cost increase over the months you should give a % instead of how to get their, however if the user askes how to get their then help them
                        Output has to be in a HTML format, and your responce will go inside an already existing div so imagine you are writing it strait into a div inside of a html page. 
                        Do not type ### at the begining of your answer or incase your answer with the ```'s or ~~~'s
                '''},
                {"role": "user", "content": f"```ALL provided Data: {data}```"}
                ])
            generated_text = client.choices[0].message.content
            addToConvo(question, fromDate, toDate, generated_text)
        except:
            return "Too Much Data! try to be smaller!"
    elif data != None and question.lower() == 'clear':
        clearConvo()
        return "Convo Cleared, Reload :D"
    else:
        return "ERROR DATA NOT LINKED"
    return generated_text

