import pandas as pd
import os
from datetime import datetime

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
    print("DATA", data)
