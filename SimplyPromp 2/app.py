import os
import sqlite3
from flask import Flask, render_template, request
from openai import OpenAI
from databaceCreator import creatingDataBace

app = Flask(__name__)

OPENAI_API_KEY = 'OPEN_AI_KEY'

@app.route("/", methods=['GET', 'POST'])
def index():
    generated_text = None
    allowToGeneratePrompt = False
    text = None
    if request.method == 'POST':
        role = request.form.get('role')
        task = request.form.get('task')
        whatfor = request.form.get('whatfor')
        please = request.form.get('please')
        example = request.form.get('example')
        text = request.form.get('text')
        outputformat = request.form.get('outputformat')

        if role != '' and task !='' and whatfor != '':
            allowToGeneratePrompt = True
            # Database operations
            conn = sqlite3.connect('Prompt-Creator/data/promptInput.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO applications VALUES (?,?,?,?,?,?,?)",(role, task, whatfor, please, example, text, outputformat))
            conn.commit()

            # OpenAI API call
            client = OpenAI(api_key=OPENAI_API_KEY)
            client = client.chat.completions.create(model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content":'''Prompt Creator,
                    Your Job is to turn the text and turn it into a good prompt the user can ask another gpt to compute. Your are not to solve the problem or task the user gives you, rather you are to take all the information provided and you format it into the best prompt you can, for another LLM to solve.
                    Here are the steps you should take:

                    1) take the information from the user and fix any errors or typos and grammar mistakes.
                    2) If information is illigibal or not enugh information is provided then just return the following and nothing else: "Please input more information or be more clear if you inputed info, and try again"
                    3) with the formated information, join it all together into one prompt that can be asked of another LLM to solve
                    4) Make sure the prompt you have created includes the following:
                            - Include the Role of GPT, modify to your plesure, but keep the same general role, an example of this is turning the role: student into Honnor student
                            - Include the task requested (Add sub-taskes if you see fit)
                            - Include what the task is going to be used for/to. expand on this if needed
                            - Format and Include Special Requests in a format easy to understand for another LLM, emphisize on the importance of using the special request
                            - Include Examples given (remember to deliver the example the way that would be easy for GPT to understand)
                            - Specifies what the output of GPT should be, you are allowed to change the output from the output givin only if not enough detail is provided or no info is provided
                            - Baced of the Role, Task and the use case of the task (For/To), infer what the tone should be, also infer the level of the task be, eg: if inputed grade 5 student as a role, dont set tone to grade 12 english level, rather set tone to grade 5 english level.
                            - IF an example is not provided, no need to make your own example, emphisize on the importance of using the example as a refrence IF provided
                    5) Make sure you are missing no information, their are not mistakes; either logical or syntax, double check all the steps, making sure you satasfy everything.
                    '''},
                    {"role": "user", "content": f"```Role: {role}\n Task: {task}\n For/To: {whatfor}\n Requests: {please}\n Examples: {example}\n  Refrense Text: {text}\nOutput format: {outputformat}```"}
                ])
            generated_text = client.choices[0].message.content
            conn = sqlite3.connect('Prompt-Creator/data/gptOutput.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO applications VALUES (?,?,?)",(task, whatfor, generated_text))
            conn.commit()
        else:
            allowToGeneratePrompt = False
            generated_text = "Please input more information or be more clear if you inputed info, and try again"

        if text != '':
            text = f"{text}"
        else:
            text = ''

    if generated_text != '' and allowToGeneratePrompt == True:
        return render_template('index.html', generated_text=generated_text, text=text, role=role, task=task, whatfor=whatfor, please=please, example=example, outputformat=outputformat)
    elif generated_text != '' and allowToGeneratePrompt == False:
        return render_template('index.html', generated_text=generated_text)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    creatingDataBace()
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 81))
    app.run(host=host, port=port)