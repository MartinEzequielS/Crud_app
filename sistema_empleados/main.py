"""
    Creamos una app con Flask sencilla pero muy flexible que conecta una base de Datos a través del servidor phpmyadmin, 
    una tabla de 4 columnas: 
    id: auto-incremental | nombre | mail | imagen 
    Con el fin de ingresar posibles empleados con todas la funciones disponibles de un CRUD. (incluido buscador)
    5 archivos HTML el cual uno funciona de Layout.

"""

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

from flaskext.mysql import MySQL

import os

from datetime import datetime


app= Flask(__name__)

mysql= MySQL()
app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_BD']="sistema"
mysql.init_app(app)  

#--------------------------------------------------------------------
# Guardamos la ruta de la carpeta "uploads" en nuestra app
CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

#setting
app.secret_key= 'mysecretkey'

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)


@app.route('/index') # '/'quiere decir pagina  principal
def index():
    sql = "SELECT * FROM `sistema`.`empleados`;"
    
    conn = mysql.connect()
    cursor = conn.cursor()   
    cursor.execute(sql)
    db_empleados = cursor.fetchall()
    conn.commit()

    #file_name=file(db_empleados[0][3])
    #imagen = os.path.join(app.config['CARPETA'],db_empleados[0][3])
    return render_template("empleados/index.html",empleados = db_empleados)
    #user_image=imagen

@app.route('/')
def create():

    return render_template('empleados/Form.html')

@app.route("/insertar", methods=['POST'])   
def insertar():

    nombre=request.form["txtnombre"]# trae el valor de la forma Clave:valor
    mail=request.form["txtnmail"]
    file=request.files["txtfile"]

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if file.filename!='':
        #...le cambiamos el nombre.
        foto=tiempo+file.filename
        # Guardamos la foto en la carpeta uploads.
        file.save("uploads/"+foto)

    values=(nombre,mail,foto)
    sql = "INSERT INTO `sistema`.`empleados` \
        (`id`, `nombre`, `correo`, `foto`) \
        VALUES (NULL, %s, %s, %s);"

    conn = mysql.connect()     # Nos conectamos a la base de datos 
    cursor = conn.cursor()     # En cursor vamos a realizar las operaciones
    cursor.execute(sql, values) # Ejecutamos la sentencia SQL en el cursor
    conn.commit()              # Hacemos el comm    

    flash("Empleado registrado con exito")
    return redirect(url_for('index'))
    #return render_template("empleados/Form.html",texto="Registro exitoso")
    #return("Regsitro exitoso")

@app.route('/delete/<id>')
def delete(id):

    conn = mysql.connect()    
    cursor = conn.cursor()    
    cursor.execute("DELETE FROM `sistema`.`empleados` WHERE id =%s", (id))
    conn.commit()           

    flash("El usuario ha sido eliminado")
    return redirect(url_for('index'))

@app.route('/get_user/<id>')
def get_user(id):
    conn = mysql.connect()    
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM `sistema`.`empleados` WHERE id =%s", (id))
    empleado = cursor.fetchall()
    return render_template("empleados/edit.html", data = empleado[0])
    

@app.route('/edit/<id>', methods=['POST'])
def edit(id):
    nombre=request.form["txtnombre"]
    mail=request.form["txtnmail"]
    file=request.form["txtfile"]
    
    sql = "UPDATE `sistema`.`empleados` \
        SET nombre= %s, correo= %s, foto=%s \
        WHERE id= %s"
    values=(nombre, mail, file, id)
    
    conn = mysql.connect()     
    cursor = conn.cursor()    
    cursor.execute('''UPDATE `sistema`.`empleados` \
        SET nombre= %s, correo= %s, foto=%s \
        WHERE id= %s''', values) 
    conn.commit()          
    flash("se ha editado correctamente")
    return redirect(url_for('index'))

#busqueda por like
@app.route('/lookup', methods=['POST'])
def lookup():
    cadena=request.form["lookup"]
    conn = mysql.connect()    
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM `sistema`.`empleados` WHERE nombre LIKE %s", ("%"+cadena+"%"))
    empleado = cursor.fetchall()
    print(empleado)
    if empleado == tuple():
        flash("No se ha encontrado coincidencia")
        return render_template("empleados/lookup.html", datos = empleado)
        
    else:
        return render_template("empleados/lookup.html", datos = empleado)



if __name__ == '__main__':
    print(main.__doc__)

    app.run(debug=True)
    
