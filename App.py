from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# initializations
app = Flask(__name__)

# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskcrud'
mysql = MySQL(app)

# settings
app.secret_key = "mysecretkey"

# routes
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('Inicio'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = '¡Usuario o contraseña incorrectos!'
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/CrudFlask/CerrarSesion')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/CrudFlask/Registrarse', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = '¡Esta cuenta ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = '¡Direccion de correo invalida!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = '¡El nombre de usuario solo debe contener caracteres y numeros!'
        elif not username or not password or not email:
            msg = '¡Por favor llene los datos!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = '¡Te has registrado con exito!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = '¡Por favor llene los datos!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/CrudFlask/Inicio')
def Inicio():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contactos')
    data = cur.fetchall()
    cur.close()
    return render_template('inicio.html', contacts = data)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contactos (nombre, telefono, email) VALUES (%s,%s,%s)", (nombre, telefono, email))
        mysql.connection.commit()
        flash('Contacto añadido exitosamente')
        return redirect(url_for('Inicio'))

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contactos WHERE id = {0}'.format(id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit-contact.html', contact = data[0])

@app.route('/update/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contactos
            SET nombre = %s,
                email = %s,
                telefono = %s
            WHERE id = %s
        """, (nombre, email, telefono, id))
        flash('Contacto actualizado exitosamente')
        mysql.connection.commit()
        return redirect(url_for('Inicio'))

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contactos WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contacto eliminado exitosamente')
    return redirect(url_for('Inicio'))
#@app.route('/pythonlogin/home')
#def home():
    # Check if user is loggedin
#    if 'loggedin' in session:
#        # User is loggedin show them the home page
#        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
#    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/CrudFlask/Perfil')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
# starting the app
if __name__ == "__main__":
    app.run(debug=True)
