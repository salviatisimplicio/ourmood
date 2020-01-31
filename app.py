from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,g
from flask_mysqldb import MySQL
#from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps


#login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:                
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function

#create flask app
app = Flask(__name__)
app.secret_key= "ourblog"

#mysql database connection
app.config["MYSQL_HOST"] = "sql7.freemysqlhosting.net"
app.config["MYSQL_USER"] = "sql7320405"
app.config["MYSQL_PASSWORD"] = "ZTh7N3S56w"
app.config["MYSQL_DB"] = "sql7320405"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

#index page
@app.route("/")
def mainpage():
    return render_template("index.html")

#register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = sha256_crypt.encrypt(request.form.get('password'))
        email = request.form.get('email')
        name = request.form.get('name')

        cursor = mysql.connection.cursor()
        sorgu="Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("login"))
            
    else:  
        return render_template("register.html")
    


#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password_enter = request.form.get('password')

        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM users WHERE username = %s"
        result = cursor.execute(sorgu,(username,))
        if result>0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_enter,real_password):
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("mainpage"))
            else:   
                return redirect(url_for("register"))   

    return render_template("login.html")




#articles
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles"
    result = cursor.execute(sorgu)
    if result>0:
        articles=cursor.fetchall()
        return render_template("articles.html",articles = articles)

    else:
        return render_template("articles.html")
    

# add article
@app.route("/addarticle",methods=["GET","POST"])
@login_required
def addarticle():
    if request.method=="POST":
        title=request.form.get("title")
        content=request.form.get("content")
        visible=request.form.get("visible")
        username=session["username"]
        
        cursor = mysql.connection.cursor()
        sorgu = "INSERT INTO articles (title,author,content) VALUES (%s,%s,%s)"
        cursor.execute(sorgu,(title,username,content,))
        mysql.connection.commit()
        cursor.close()

    return render_template("add-article.html")

#article details
@app.route("/article/<string:id>")
def article_full(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where id = %s"
    result = cursor.execute(sorgu,(id,))

    if result > 0 :
        article = cursor.fetchone()
        return render_template("article-full.html",article = article)
    else:
        return render_template("article-full.html")

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("mainpage"))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)














