from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, TextField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, EqualTo
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
    except mysql.connector.Error as e:
        print(f'The error "{e}" occurred')

    return connection


def execute_db_query(query, params=None):
    conn = create_db_connection(sql_host, sql_user, sql_pass, sql_db)
    cursor = conn.cursor()
    if params is not None:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()
    conn.close()


def retrieve_db_query(query, params=None):
    conn = create_db_connection(sql_host, sql_user, sql_pass, sql_db)
    cursor = conn.cursor()
    if params is not None:
        cursor.execute(query, params) 
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    names = [c[0] for c in cursor.description]
    conn.close()
    return results, names


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

    def check_pass(self, password):
        return bcrypt.checkpw(password.encode(), self.pass_hash)

    def authenticate(self, password):
        if self.exists:
            self.is_authenticated = self.check_pass(password)
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
        hashed = bcrypt.hashpw(self.password.data.encode(), bcrypt.gensalt())
        execute_db_query("INSERT INTO Account (userName, type, passHash) VALUES (%s, 3, %s)", (self.username.data, hashed,))
        return True

    def clear(self):
        self.username.data = None
        self.password.data = None


class ChangePassForm(FlaskForm):
    curr_pass = PasswordField('Old Password', validators=[DataRequired()])
    new_pass = PasswordField('New Password', validators=[DataRequired()])
    new_pass_conf = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('new_pass', message='New passwords must match')])
    submit = SubmitField('Log In')

    def __init__(self, user, *args, **kwargs):
        super(ChangePassForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate(self):
        if not self.user.exists:
            return False
        elif not self.user.check_pass(self.curr_pass.data):
            return False
        else:
            hashed = bcrypt.hashpw(self.new_pass.data.encode(), bcrypt.gensalt())
            execute_db_query('UPDATE Account SET passHash = %s WHERE userName LIKE %s', (hashed, self.user.get_id(),))
            return True


class EditItemForm(FlaskForm):
    name_field = TextField('Name', validators=[DataRequired()])
    type_field = SelectField(label='Type', choices=retrieve_db_query('SELECT * FROM Type;')[0], validators=[DataRequired()])
    qty_field = TextField('Quantity')
    units_field = TextField('Units')
    location = SelectField(label='Location', choices=retrieve_db_query('SELECT * FROM Location;')[0], validators=[DataRequired()])
    expire_field = DateField('Expiration Date')
    public_field = BooleanField('Public')
    submit = SubmitField('Create')
    action = 'create'
    item_id = 0

    def __init__(self, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        if 'attrs' in kwargs:
            self.action = 'edit'
            attrs = kwargs['attrs']
            self.item_id = attrs['itemID']
            self.name_field.data = attrs['name']
            self.type_field.data = attrs['type']
            self.qty_field.data = attrs['qty']
            self.units_field.data = attrs['units']
            self.location.data = attrs['location']
            self.expire_field.data = attrs['expirationDate']
            self.public_field.data = attrs['public']

    def insert(self):
        sql_string = 'INSERT INTO Item (name, type, location, public, qty, units, expirationDate) VALUES (%s, %s, %s, %s, %s, %s, %s);'
        params = (self.name_field.data, self.type_field.data, self.location.data, self.public_field.data, self.qty_field.data, self.units_field.data, self.expire_field.data)
        try:
            execute_db_query(sql_string, params)
            return True
        except Exception as e:
            print(e)
            return False

    def update(self, item_id):
        sql_string = 'UPDATE Item SET name = %s, type = %s, location = %s, public = %s, qty = %s, units = %s, expirationDate = %s WHERE itemID = %s;'
        params = (self.name_field.data, self.type_field.data, self.location.data, self.public_field.data, self.qty_field.data, self.units_field.data, self.expire_field.data, item_id)
        try:
            execute_db_query(sql_string, params)
            return True
        except Exception as e:
            print(e)
            return False

    def clear(self):
            self.item_id = None
            self.name_field.data = None
            self.type_field.data = 0
            self.qty_field.data = None
            self.units_field.data = None
            self.location.data = 0
            self.expire_field.data = None
            self.public_field.data = False

class EditUserForm(FlaskForm):
    name_field = TextField('userName', validators=[DataRequired()])
    type_field = SelectField(label='type', choices=retrieve_db_query('SELECT * FROM AccountType;')[0], validators=[DataRequired()])
    pass_field = PasswordField('new password')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        if 'attrs' in kwargs:
            attrs = kwargs['attrs']
            self.user_id = attrs['userID']
            self.name_field.data = attrs['userName']
            self.type_field.data = attrs['type']

    def update(self, user_id):
        if self.pass_field.data is not None and self.pass_field.data != '':
            hashed = bcrypt.hashpw(self.pass_field.data.encode(), bcrypt.gensalt())
            sql_string = 'UPDATE Account SET userName = %s, type = %s, passHash = %s WHERE userID = %s;'
            params = (self.name_field.data, self.type_field.data, hashed, user_id)
        else:
            sql_string = 'UPDATE Account SET userName = %s, type = %s WHERE userID = %s'
            params = (self.name_field.data, self.type_field.data, user_id)
        try:
            execute_db_query(sql_string, params)
            return True
        except Exception as e:
            print(e)
            return False

