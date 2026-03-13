from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
from mysql.connector import Error
import config
import os

app = Flask(__name__)


def get_db_connection():
    try:
        return mysql.connector.connect(
            host=getattr(config, 'MYSQL_HOST', os.getenv('DB_HOST', '127.0.0.1')),
            user=getattr(config, 'MYSQL_USER', os.getenv('DB_USER', 'root')),
            password=getattr(config, 'MYSQL_PASSWORD', os.getenv('DB_PASSWORD', '')),
            database=getattr(config, 'MYSQL_DB', os.getenv('DB_NAME', 'votaciones')),
        )
    except Error:
        raise


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/registro', methods=['GET'])
def registro():
    success = request.args.get('success')
    error = request.args.get('error')
    msg = request.args.get('msg')
    cedula = request.args.get('cedula')
    return render_template('registro.html', success=success, error=error, msg=msg)


@app.route('/consultar', methods=['GET', 'POST'])
def consultar():
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        if not cedula:
            return render_template('consultar.html', error='Debe indicar la cédula')
        return redirect(url_for('resultado', cedula=cedula))
    return render_template('consultar.html')


@app.route('/resultado', methods=['GET', 'POST'])
def resultado():
    cedula = None
    if request.method == 'POST':
        cedula = request.form.get('cedula')
    else:
        cedula = request.args.get('cedula')

    if not cedula:
        return render_template('resultado.html')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT nombre, ciudad, departamento, puesto, mesa FROM votantes WHERE cedula = %s LIMIT 1"
        cursor.execute(sql, (cedula,))
        row = cursor.fetchone()
        if row:
            nombre, ciudad, departamento, puesto, mesa = row
            return render_template('resultado.html', nombre=nombre, ciudad=ciudad, departamento=departamento, puesto=puesto, mesa=mesa)
        else:
            return render_template('resultado.html', error='No se encontró votante con esa cédula', cedula=cedula)
    except Error as err:
        return render_template('resultado.html', error='Error al consultar: ' + str(err))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/guardar', methods=['POST'])
def guardar():
    cedula = request.form.get('cedula')
    nombre = request.form.get('nombre')
    ciudad = request.form.get('ciudad')
    departamento = request.form.get('departamento')
    puesto = request.form.get('puesto')
    mesa_raw = request.form.get('mesa')

    if not cedula or not nombre:
        return jsonify({'error': 'cedula y nombre son obligatorios'}), 400

    try:
        mesa = int(mesa_raw) if mesa_raw not in (None, '') else None
    except ValueError:
        return jsonify({'error': 'mesa debe ser un número entero'}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = (
            "INSERT INTO votantes (cedula, nombre, ciudad, departamento, puesto, mesa) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(sql, (cedula, nombre, ciudad, departamento, puesto, mesa))
        conn.commit()
    except Error as err:
        if conn:
            conn.rollback()
        err_no = getattr(err, 'errno', None)
        if err_no == 1062:
            return redirect(url_for('registro', error=1, msg='Cédula ya registrada', cedula=cedula))
        return redirect(url_for('registro', error=1, msg=str(err), cedula=cedula))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('registro', success=1))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
