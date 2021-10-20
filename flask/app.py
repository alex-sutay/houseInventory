from flask import Flask, render_template, session
import mysql.connector
from mysql.connector import Error
from config import sql_host, sql_user, sql_pass, sql_db, secret_key


app = Flask(__name__)
app.secret_key = secret_key


def create_db_connection(hostname, username, password, db):
    connection = None
    try:
        connection = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=password,
                database=db)
        print('Connection successful')
    except Error as e:
        print(f'The error "{e}" occurred')

    return connection


def get_table(table):
    conn = create_db_connection(sql_host, sql_user, sql_pass, sql_db)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')  # TODO kinda sql-injection-ish, find a better way to do this 
    results = cursor.fetchall()
    names = [c[0] for c in cursor.description]
    conn.close()
    return results, names


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/groceries')
def groceries():
    res, names = get_table('Groceries')
    return render_template('show_table.html', table_name='Groceries', results=res, columns=names)


@app.route('/all')
def all_items():
    res, names = get_table('AllItems')
    return render_template('show_table.html', table_name='All Items', results=res, columns=names)


@app.route('/projects')
def projects():
    res, names = get_table('ActiveProjects')
    return render_template('show_table.html', table_name='Active Projects', results=res, columns=names)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

