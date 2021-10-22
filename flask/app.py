from flask import Flask, render_template, session, request, flash, url_for, redirect
import mysql.connector
from mysql.connector import Error
from config import sql_host, sql_user, sql_pass, sql_db, secret_key
from models import create_db_connection, User, users, LoginForm, ensure_auth_level, MakeUserForm


app = Flask(__name__)
app.secret_key = secret_key


def get_table(table):
    conn = create_db_connection(sql_host, sql_user, sql_pass, sql_db)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')  # TODO kinda sql-injection-ish, find a better way to do this 
    results = cursor.fetchall()
    names = [c[0] for c in cursor.description]
    conn.close()
    return results, names


@app.route('/')
@ensure_auth_level(5)
def index():
    return render_template('index.html')


@app.route('/groceries')
@ensure_auth_level(2)
def groceries():
    res, names = get_table('Groceries')
    return render_template('show_table.html', table_name='Groceries', results=res, columns=names)


@app.route('/all')
@ensure_auth_level(2)
def all_items():
    res, names = get_table('AllItems')
    return render_template('show_table.html', table_name='All Items', results=res, columns=names)


@app.route('/projects')
@ensure_auth_level(2)
def projects():
    res, names = get_table('ActiveProjects')
    return render_template('show_table.html', table_name='Active Projects', results=res, columns=names)


@app.route('/public')
@ensure_auth_level(3)
def public_inventory():
    res, names = get_table('PublicGroceries')
    return render_template('show_table.html', table_name='Snacks and Drinks', results=res, columns=names)


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            users[form.user.get_id()] = form.user
            session['user'] = form.user.get_id()
            flash('login successful')
            return redirect(url_for('index'))
        else:
            flash('login failed')
    return render_template('login.html', form=form)


@app.route('/manageusers', methods=['GET', 'POST'])
@ensure_auth_level(1)
def manage_users_post():
    form = MakeUserForm()
    if request.method == 'POST' and form.validate():
        if form.validate():
            flash('User created successfully')
        else:
            flash('User creation failed')
    return render_template('manageusers.html', form=form)


@app.route('/logout')
@ensure_auth_level(3)
def logout():
    users.pop(session['user'])
    session.pop('user')
    return redirect(url_for('index'))


@app.context_processor
def get_current_user():
    user = users[session['user']] if 'user' in session else User('')
    return {"current_user": user}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)

