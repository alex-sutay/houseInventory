from flask import Flask, render_template, session, request, flash, url_for, redirect
import mysql.connector
from mysql.connector import Error
from config import sql_host, sql_user, sql_pass, sql_db, secret_key
from models import retrieve_db_query, User, users, LoginForm, ensure_auth_level, MakeUserForm, ChangePassForm, InsertItemForm


app = Flask(__name__)
app.secret_key = secret_key


def get_table(table):
    return retrieve_db_query(f'SELECT * FROM {table}')  # TODO kinda sql-injection-ish, find a better way to do this 


@app.route('/')
@ensure_auth_level(5)
def index():
    return render_template('index.html')


@app.route('/groceries')
@ensure_auth_level(2)
def groceries():
    res, names = get_table('Groceries')
    return render_template('show_table.html', table_name='Groceries', results=res, columns=names)


@app.route('/all', methods=['GET', 'POST'])
@ensure_auth_level(2)
def all_items():
    form = InsertItemForm()
    if request.method == 'POST':
        if form.validate():
            flash('Item Created')
        else:
            flash('Item creation failed')
    res, names = get_table('AllItems')
    return render_template('show_table_items.html', table_name='All Items', results=res, columns=names, form=form)


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
    if request.method == 'POST':
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


@app.route('/changepass', methods=['GET', 'POST'])
@ensure_auth_level(3)
def change_pass_post():
    form = ChangePassForm(users[session['user']])
    if request.method == 'POST' and form.validate():
        flash('Password updated')
    return render_template('changepass.html', form=form)


@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.context_processor
def get_current_user():
    user = users[session['user']] if 'user' in session else User('')
    return {"current_user": user}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)

