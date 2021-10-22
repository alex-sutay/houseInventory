from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, TextField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import ValidationError
import mysql.connector
from config import sql_host, sql_user, sql_pass, sql_db
import bcrypt
from functools import wraps
from flask import abort, session


users = dict()


def ensure_auth_level(perm_needed):
    def ensure_auth_level_outer(fn):
        @wraps(fn)
        def ensure_auth_level_inner(*args, **kwargs):
            userid = session['user'] if 'user' in session else ''
            user = users[userid] if userid in users else User('')
            if user.perm_level > perm_needed:
                abort(401)
            else:
                return fn(*args, **kwargs)
        return ensure_auth_level_inner
    return ensure_auth_level_outer


def create_db_connection(hostname, username, password, db):
    connection = None
    try:
        connection = mysql.connector.connect(
                host=hostname,
                user=username,
                passwd=password,
                database=db,
                auth_plugin='mysql_native_password')
        print('Connection successful')
    except mysql.connector.Error as e:
        print(f'The error "{e}" occurred')

    return connection


class User():
    def __init__(self, username):
        self.username = username
        self.is_authenticated = False
        self.is_active = True
        self.is_anonymous = False
        # fetch the user information
        conn = create_db_connection(sql_host, sql_user, sql_pass, sql_db)
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Account WHERE userName LIKE %s;', (username,))
            row = cursor.fetchone()
            if row:
                self.exists = True
                self.pass_hash = bytes(row[3])
                self.perm_level = row[2]
            else:
                self.exists = False
                self.pass_hash = b''
                self.perm_level = 5
            conn.close()
        else:
            self.exists = False
            self.pass_hash = b''
            self.perm_level = 5

    def get_id(self):
        return self.username

    def authenticate(self, password):
        if self.exists:
            self.is_authenticated = bcrypt.checkpw(password.encode(), self.pass_hash)
        else:
            self.is_authenticated = False
        return self.is_authenticated



class LoginForm(FlaskForm):
    username = TextField('User', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        self.user = User(self.username.data)
        # if not initial_validation:
        #     return True
        if not self.user.exists:
            # self.username.errors.append('Invalid user/password')
            return False
        if not self.user.authenticate(self.password.data):
            # self.password.errors.append('Invalid user/password')
            return False
        return True


class MakeUserForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super(MakeUserForm, self).__init__(*args, **kwargs)

    def validate(self):
        conn = create_db_connection(sql_host, sql_user, sql_pass, sql_db)
        if conn is not None:
            cursor = conn.cursor()
            hashed = bcrypt.hashpw(self.password.data.encode(), bcrypt.gensalt())
            cursor.execute("INSERT INTO Account (userName, type, passHash) VALUES (%s, 3, %s)", (self.username.data, hashed,))
            conn.commit()
            conn.close()
            return True
        else:
            return False

