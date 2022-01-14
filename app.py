#  .\env\Scripts\Activate.ps1
#   python app.py

from random import randint

import yaml
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL

# creating the Flask instance.
app = Flask(__name__)

#fetching secret info
db = yaml.safe_load(open('db.yaml'))
app.secret_key = "labib"

# Configure mail
app.config['MAIL_SERVER'] = db['mail_server']
app.config['MAIL_PORT'] = db['mail_port']
app.config['MAIL_USERNAME'] = db['mail_username']
app.config['MAIL_PASSWORD'] = db['mail_password']
app.config['MAIL_USE_TLS'] = db['mail_use_tls']
app.config['MAIL_USE_SSL'] = db['mail_use_ssl']
mail = Mail(app)
otp = randint(000000, 999999)

# Configure db
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)

name = ""
email = ""
password = ""


@app.route("/", methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    query = "SELECT DISTINCT batch FROM student ORDER BY batch"
    cur.execute(query)
    batches = cur.fetchall()
    if request.method == 'POST':
        global email
        email = request.form["email"]
        global password
        password = request.form["password"]
        cur = mysql.connection.cursor()
        checkName = cur.execute(
            "SELECT * FROM admin WHERE email = %s", [email])
        if checkName == 1:
            checkPassword = cur.execute(
                "SELECT * FROM admin WHERE email = %s && password = %s", [email, password])
            if checkPassword == 1:
                record = cur.fetchone()
                session['admin_id'] = record[0]
                session['admin_name'] = record[1]
                session['admin_email'] = record[2]
                session['logged_in'] = True
                return render_template("index.html", batches=batches)
            else:
                error = "Wrong password inserted!"
        else:
            error = "User not found!"
        return render_template("error.html", error=error)
    else:
        return render_template("index.html", batches=batches)

# goto about page
@app.route("/about")
def about():
    return render_template("about.html")


# goto register page
@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")

# goto sign_in page
@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")


# goto sign_out page
@app.route("/sign_out")
def sign_out():
    session.pop('logged_in')
    session['logged_in'] = False
    return redirect("/")

# sending otp to email


@app.route("/sendOTP", methods=['GET', 'POST'])
def sendOTP():
    if request.method == 'POST':
        global name
        name = request.form["name"]
        global email
        email = request.form["email"]
        global password
        password = request.form["password"]
        cur = mysql.connection.cursor()
        checkEmail = cur.execute(
            "SELECT email FROM admin WHERE email = %s", [email])
        if checkEmail > 0:
            error = "Email already exits"
            return render_template("error.html", error=error)
        else:
            msg = Message('OTP Varification of admin sign-up.', sender='unetwork.varification@gmail.com',recipients=[email])
            msg.body = "Hey {0}!\r\n \r\n A sign in attempt requires further verification because we did not recognize your device. \r\n To complete the sign in, enter the verification code on the unrecognized device.\r\n \r\n Verification code: {1}\r\n \r\n If you did not attempt to sign in to your account, then ignore it. \r\n \r\n Thanks,\r\n The UODA-Grading Team\r\n".format(name,str(otp))
            mail.send(msg)
            return render_template("verify.html", email=email)
    else:
        return redirect("/")

# check if otp match


@app.route('/verify', methods=['POST', "GET"])
def varify():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        cur = mysql.connection.cursor()
        cur.execute(
              "INSERT INTO admin(name, email, password) VALUES(%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()
        session['admin_name'] = name
        session['logged_in'] = True
        return redirect("/")
    else:
        error = "OTP Not Matched !"
        return render_template("error.html", error=error)

# goto batch page
@app.route('/batch/<batch>')
def batch(batch):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student, b_{0} WHERE student.batch = '{0}' AND b_{0}.std_id = student.std_id  ORDER BY student.std_id".format(
        batch)
    cur.execute(query)
    students = cur.fetchall()
    query = "SELECT * FROM b_{0}".format(batch)
    cur.execute(query)
    courseName = [i[0] for i in cur.description]
    return render_template("batch.html", students=students, courseName=courseName)

# goto ranking page
@app.route('/ranks')
def ranks():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student LIMIT 11"
    cur.execute(query)
    students = cur.fetchall()
    return render_template("ranks.html", students=students)
    # return str(students)

# goto student page
@app.route("/student")
def search():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student ORDER BY std_name LIMIT 10"
    cur.execute(query)
    students = cur.fetchall()
    return render_template("student.html", students=students)


# livesearch
@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    searchbox = request.form.get("text")
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student WHERE std_name LIKE '{0}%' OR std_name LIKE '%{0}%' OR std_name LIKE '%{0}' OR std_id LIKE '{0}%' OR std_id LIKE '%{0}%' OR std_id LIKE '%{0}'  ORDER BY std_name DESC Limit 9".format(
        searchbox)
    cur.execute(query)
    result = cur.fetchall()
    return jsonify(result)

# goto edit page
@app.route('/edit/<batch>/<std_id>')
def edit(batch, std_id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student, b_{0} WHERE student.std_id = '{1}' AND b_{0}.std_id = '{1}'".format(
        batch, std_id)
    cur.execute(query)
    students = cur.fetchone()
    columnName = [i[0] for i in cur.description]
    return render_template("edit.html", students=students, columnName=columnName)
    # return query

# do updating
@app.route('/update', methods=['POST'])
def update():
    query = request.form["q"]
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return str(query)

# goto add page
@app.route('/add/<batch>')
def add(batch):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student, b_{} LIMIT 1".format(batch)
    cur.execute(query)
    columnName = [i[0] for i in cur.description]
    return render_template("add.html", columnName=columnName,batch=batch)

@app.route('/new_add')
def new_add():
    cur = mysql.connection.cursor()
    query = "SELECT DISTINCT batch FROM student"
    cur.execute(query)
    batches = cur.fetchall()
    query = "SELECT * FROM student"
    cur.execute(query)
    students = cur.fetchall()
    return render_template("new_add.html",batches=batches,students=students)

@app.route('/new_add_get_course', methods=["POST", "GET"])
def new_add_get_course():
    batch = request.form.get("batch")
    cur = mysql.connection.cursor()
    query = "SELECT * FROM b_{0}".format(batch)
    cur.execute(query)
    columnName = [i[0] for i in cur.description]
    return str(columnName)

@app.route('/new_add_get_id', methods=["POST", "GET"])
def new_add_get_id():
    name = request.form.get("name")
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student WHERE std_name = '{}'".format(name)
    cur.execute(query)
    student_table=cur.fetchone()
    return str(student_table)

@app.route('/replace', methods=['POST'])
def replace():
    delete_batch_query = request.form["delete_batch_query"]
    std_query = request.form["std_query"]
    batch_query = request.form["batch_query"]
    
    cur = mysql.connection.cursor()
    cur.execute(delete_batch_query)
    cur.execute(std_query)
    cur.execute(batch_query)
    mysql.connection.commit()
    cur.close()
    return "OK"
# goto batch page
@app.route('/generate/<batch>/<std_id>')
def generate(batch,std_id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM student, b_{0} WHERE student.std_id = '{1}' AND b_{0}.std_id = '{1}'".format(
        batch,std_id)
    cur.execute(query)
    students = cur.fetchall()
    query = "SELECT * FROM b_{0}".format(batch)
    cur.execute(query)
    courseName = [i[0] for i in cur.description]
    return render_template("generate.html", students=students, courseName=courseName)
    # return query
    

# do adding
@app.route('/adding', methods=['POST'])
def adding():
    std_query = request.form["std_query"]
    batch_query = request.form["batch_query"]
    cur = mysql.connection.cursor()
    cur.execute(std_query)
    cur.execute(batch_query)
    mysql.connection.commit()
    cur.close()
    return "ok"

# do deleting
@app.route('/delete/<batch>/<std_id>')
def delete(batch,std_id):
    cur = mysql.connection.cursor()
    query = "DELETE FROM `student` WHERE std_id = '{}'".format(std_id)
    cur.execute(query)
    query = "DELETE FROM `b_{0}` WHERE std_id = '{1}'".format(batch,std_id)
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return redirect("/batch/",batch)

if __name__ == "__main__":
    app.run(debug=True)
