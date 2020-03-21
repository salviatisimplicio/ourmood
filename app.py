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
app.config["MYSQL_HOST"] = *******
app.config["MYSQL_USER"] =  *******
app.config["MYSQL_PASSWORD"] =  *******
app.config["MYSQL_DB"] = *******
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
    sorgu = "SELECT * FROM articles ORDER BY id DESC"
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
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="editor" or data["statu"]=="admin":
        if request.method=="POST":
            title=request.form.get("title")
            content=request.form.get("content")
            visible=request.form.get("visible")
            username=session["username"]

            cursor = mysql.connection.cursor()
            sorgu = "INSERT INTO articles (title,author,content,visible) VALUES (%s,%s,%s,%s)"
            cursor.execute(sorgu,(title,username,content,visible,))
            mysql.connection.commit()
            cursor.close()

            return render_template("add-article.html")
        else:
            return render_template("add-article.html")

    else:
        return redirect(url_for("mainpage"))


@app.route("/dashboard")
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="editor" or data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where author = %s"
        result = cursor.execute(sorgu,(session["username"],))

        if result > 0:
            articles = cursor.fetchall()
            return render_template("dashboard.html",articles = articles)
        else:
            return render_template("dashboard.html")
    else:
        return redirect(url_for("mainpage"))


#article details
@app.route("/article/<string:id>",methods=["GET","POST"])
def article_full(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where id = %s"
    result = cursor.execute(sorgu,(id,))

    cursor2=mysql.connection.cursor()
    sorgu2="Select * from comments where toarticle=%s"
    cursor2.execute(sorgu2,(id,))

    if result > 0 :
        article = cursor.fetchone()
        comments = cursor2.fetchall()
        return render_template("article-full.html",article = article,comments=comments)
    else:
        return render_template("article-full.html")





@app.route("/addcomment/<string:id>",methods=["GET","POST"])
@login_required
def addcomment(id):
        #tourl= str(request.path)
        #tourllist=tourl.split("/")
        #toarticle=tourllist[2]

        content=request.form.get("content")
        username=session["username"]
        cur= mysql.connection.cursor()
        sor = "INSERT INTO comments (author,content,toarticle) VALUES (%s,%s,%s)"
        cur.execute(sor,(username,content,id,))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("article_full", id= id))


#delete article
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where author = %s and id = %s"
    result = cursor.execute(sorgu,(session["username"],id))
    if result>0:
        deletesorgu = "Delete from articles where id = %s "
        cursor.execute(deletesorgu,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("mainpage"))
#update
@app.route("/edit/<string:id>")
@login_required
def update(id):
    return render_template("update.html")






@app.route("/articleadminnnnnnnnnnnnn")
@login_required
def articleadmin():
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles"
        result = cursor.execute(sorgu)

        if result > 0:
            articles = cursor.fetchall()
            return render_template("articleadmin.html",articles = articles)
        else:
            return render_template("articleadmin.html")
    else:
        return redirect(url_for("mainpage"))



@app.route("/deleteeeeeeeeeeee/<string:id>")
@login_required
def deletee(id):
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        deletesorgu = "Delete from articles where id = %s"
        cursor.execute(deletesorgu,(id,))
        mysql.connection.commit()
        return redirect(url_for("articleadmin"))
    else:
        return redirect(url_for("mainpage"))



@app.route("/useradminnnnnnnnnnnnn")
@login_required
def useradmin():
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()

    if data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from users"
        result = cursor.execute(sorgu)

        if result > 0:
            users = cursor.fetchall()
            return render_template("useradmin.html",users = users)
        else:
            return render_template("useradmin.html")

    else:
        return redirect(url_for("mainpage"))

@app.route("/deleteeeeeeeeeeeeuser/<string:id>")
@login_required
def deleteuser(id):
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        deleteusersorgu = "Delete from users where id = %s"
        cursor.execute(deleteusersorgu,(id,))
        mysql.connection.commit()
        return redirect(url_for("useradmin"))
    else:
        return redirect(url_for("mainpage"))


@app.route("/seteditor/<string:id>")
@login_required
def seteditor(id):
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        seteditor = "UPDATE users SET statu='editor' WHERE id=%s"
        cursor.execute(seteditor,(id,))
        mysql.connection.commit()
        return redirect(url_for("useradmin"))
    else:
        return redirect(url_for("mainpage"))


@app.route("/setadmin/<string:id>")
@login_required
def setadmin(id):
    cur = mysql.connection.cursor()
    sor = "select * from users where username = %s"
    cur.execute(sor,(session["username"],))
    data = cur.fetchone()
    if data["statu"]=="admin":
        cursor = mysql.connection.cursor()
        setadmin = "UPDATE users SET statu='admin' WHERE id=%s"
        cursor.execute(setadmin,(id,))
        mysql.connection.commit()
        return redirect(url_for("useradmin"))
    else:
        return redirect(url_for("mainpage"))



#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("mainpage"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)














