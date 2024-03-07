import sqlite3

def creatingDataBace():
    #USER INPUT DATABACE
    conn = sqlite3.connect('Prompt-Creator/data/promptInput.db', check_same_thread=False)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS applications (
        role TEXT,
        task TEXT,
        whatfor TEXT,
        please TEXT,
        example TEXT,
        text TEXT,
        outputformat TEXT
    )"""

    cursor.execute(create_table_query)
    conn.commit()

    #GPT OUTPUT DADABACE CREATED

    conn = sqlite3.connect('Prompt-Creator/data/gptOutput.db', check_same_thread=False)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS applications (task TEXT, whatfor TEXT, generated_text TEXT)"""
    cursor.execute(create_table_query)
    conn.commit()
