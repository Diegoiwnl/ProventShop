from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_login import LoginManager
from functools import wraps
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = '08400840'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Agenda2024"
)

cursor = db.cursor()


def encripcontra(password):
    # Generar un hash de la contraseña
    encriptar = generate_password_hash(password)
    return encriptar

class Usuario:
    def __init__(self, id, nombrecli, email):
        self.id = id
        self.nombrecli = nombrecli
        self.email = email
        

@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor()
    query = "SELECT * FROM registro WHERE id = %s"
    cursor.execute(query, (user_id))
    user_data = cursor.fetchone()

    if user_data:
        user = Usuario (id=user_data[0], nombrecli=user_data[2], email=user_data[4])
        return user
    else:
        return None

    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Debes iniciar sesión primero.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():

        if request.method == 'POST':
            username = request.form ['txt']
            email = request.form['Email']
            password = request.form['pswd']

            if not username or not email or not password:
                flash('Por favor, completa todos los campos.', 'danger')
                return render_template('register.html')
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            cursor = db.cursor()
            query = "INSERT INTO registro (nombrecli, email, contracli) VALUES (%s, %s, %s)"
            values = (username, email, hashed_password)
            cursor.execute(query, values)
            db.commit()

            flash('Usuario registrado correctamente!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']

        cursor = db.cursor()
        query = "SELECT * FROM registro WHERE email = %s AND contracli = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            flash('Inicio de sesion exitoso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo electronico o contraseña incorrectos.', 'danger')

    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about') 
def about():
    return render_template('about.html')


@app.route('/menu')
def menu():
    return render_template('menu.html')


logging.basicConfig(level=logging.DEBUG)

@app.route('/reservation', methods= ['GET', 'POST'])
def reservation():
    if request.method == 'POST':
        cod_mesa = request.form['cod_mesa']
        num_sillas = request.form['num_sillas']
        fecha_reserva = request.form['fecha_reserva']
        horario_reserva = request.form['horario_reserva']

        if not cod_mesa.isdigit() or not num_sillas.isdigit():
            flash('Por favor, ingresa numeros validos para el codigo de mesa y el numero de sillas.', 'danger')
            return render_template ('success.html')
        

        cursor = db.cursor()
        query = "INSERT INTO reservas(codmesa, numerosillas, fechareserva, horarioreserva) VALUES (%s, %s, %s, %s)"
        values = (cod_mesa, num_sillas, fecha_reserva, horario_reserva)
        cursor.execute(query, values)
        db.commit()

        logging.debug("Procesando reserva...")
        
        flash('Reserva creada exitosamente!', 'success')
        return redirect(url_for('success'))
    
    return render_template('reservation.html')

@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')


@app.route('/servicio')
def servicio():
    return render_template('service.html')



app.run(debug=True, port=5005)