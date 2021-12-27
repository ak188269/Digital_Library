import re
from types import MethodDescriptorType
from flask import Flask ,render_template, url_for,flash,request,redirect,session
from datetime import date
import firebase_admin
from firebase_admin import credentials , auth,db
from flask_mail import Mail, Message
import random
import os
from werkzeug.utils import secure_filename
pin=26
app=Flask(__name__)
app.secret_key = 'the random string'
#firebase configuration
firebaseConfig = {
  "apiKey": "",
  "authDomain": "",
"projectId": "",
  "storageBucket": "",
 " messagingSenderId": "",
  "appId": "",
  "measurementId": ""
}
#firebase initilization

cred = credentials.Certificate("mysite/static/serviceAccountKey.json")
# cred = credentials.Certificate("static/serviceAccountKey.json")

# firebase_admin.initialize_app(cred)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'your_database_url_from_firebase'
})
ref = db.reference('users')
#mail configuration
mail = Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'example123@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config["UPLOAD_PATH"]="mysite/static/uploads"
@app.route("/")
def home():
    if 'user' in session:
        return render_template("index.html",date=date.today().year,user_name=session["user"])
    return render_template("index.html",date=date.today().year)
@app.route("/login",methods=["POST","GET"])
def login():
    if 'user' in session:

        return redirect(url_for('books'))

    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        if str(email).find(".")>str(email).find("@") :
            user=str(email).split("@")[0]
        else :
            user=str(email).split(".")[0]

        user1=ref.order_by_key().get()
        key=user1.keys()
        if  user in key and user1[user]["email"]==email and user1[user]["password"]==password:
            session['user']=user1[user]["user_name"]
            # flash("Welcome ",{user1[user]["user_name"]})
            # return render_template("books.html",user_name=user1[user]["user_name"])
            return redirect(url_for("books"))
        else :
            flash("Wrong Credentials Try again")
            return render_template("login.html")
    # flash('You have to login first')
    return render_template("login.html")
@app.route("/books")
def books():
    if "user" in session:
        refere=db.reference("books")
        books=refere.get()
        return render_template("books.html",user_name=session["user"],books=books)
    return redirect("login")
@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")
        confrim_password=request.form.get("confirm_password")
        user_name=request.form.get("user_name")
        phone=request.form.get("number")
        if str(email).find(".")>str(email).find("@") :
            user_id=str(email).split("@")[0]
        else :
            user_id=str(email).split(".")[0]
        # ref=db.reference("users")
        user1=ref.order_by_key().get()
        key=user1.keys()
        if  str(user_id) in key:
            flash("email already exit try another ")
            return render_template("login.html")
        else :
            if password!=confrim_password:
                flash("Your password and confirm password did not match")
                return render_template("register.html")
            else:
                ref.child(user_id).set({
                "email":email,
                "password":password,
                "user_name":user_name,
                "phone":phone
                })
            # user = auth.create_user(
            # email=email,
            # password=password,
            # email_verified=False,
            # display_name='John Doe',
            # photo_url='http://www.example.com/12345678/photo.png',
            #             disabled=False)
            # print('Sucessfully created new user: {0}'.format(user.uid))
                flash("succesfully created account")
                return render_template("login.html")
    # else :
    #     return render_template("register.html")
    return render_template("register.html")
@app.route("/forget",methods=["POST",'GET'])
def forget_password():
    if request.method=="POST":
        email=request.form.get("email")
        key=ref.order_by_key().get().keys()
        if str(email).find(".")>str(email).find("@") :
            user_id=str(email).split("@")[0]
        else :
            user_id=str(email).split(".")[0]
        if user_id in key:
            global pin
            otp=random.randint(100000,600000)
            pin=otp
            msg = Message(
                    'Password Reset',
                    sender ="example@gmail.com",
                    recipients = [str(email)],
                )
            msg.body = f"We have been requested for password change. If you have not requested please contact us .Your otp is {otp}"
            mail.send(msg)
            return render_template("otp.html")
        else:
            flash("email dosen`t exit")
            return redirect(url_for("login"))
        # send_custom_email(email, link)
    else :
        return render_template("forgetpassword.html")
    return redirect(url_for("login"))
@app.route("/reset",methods=["POST","GET"])
def resetpassword():
    if request.method=="POST":
        otp=request.form.get("otp")
        if str(pin)==otp:
            return render_template("newpassword.html")
        else:
            flash(f"Wrong otp ")
            return render_template("otp.html")
    return redirect(url_for("login"))

@app.route("/newpassword",methods=["POST","GET"])
def newpassword():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        confirm_password=request.form.get("confirm_password")
        if password!=confirm_password:
            flash("Password and confirm Password are not same ")
            return render_template("newpassword.html")
        else :
            if str(email).find(".")>str(email).find("@") :
                user_id=str(email).split("@")[0]
            else :
                user_id=str(email).split(".")[0]
            # ref=db.reference("users")
            ref.child(user_id).update({
                        "password":password
                    })
            flash("Password changed successfully")
            return redirect(url_for("login"))
    return redirect(url_for("login"))
@app.route('/logout')
def log_out():
    if 'user' in session:
        session.pop('user')
        flash('Loged out Successfully')
        return  redirect(url_for('home'))
        # return render_template("index.html")
    return  redirect(url_for('login'))
@app.route("/message",methods=['POST','GET'])
def message():
    if request.method=="POST":
        name=request.form.get("name")
        mobile=request.form.get("number")
        email=request.form.get("email")
        message=request.form.get("message")
        refe=db.reference("response")
        refe.child(name).set({
            "name":name,
            "mobile":mobile,
            "email":email,
            "message":message
        })
        flash("Message sent successfully")
        return redirect(url_for("home"))
    return redirect(url_for("home"))
@app.route('/upload',methods=['GET','POST'])
def upload():
    if 'user' in session:
        if request.method=='POST':
            book_name=request.form.get("book_name")
            about=request.form.get("about")
            for file in request.files.getlist('file_name'):
                            # file=request.files['file_name']  #(this is used when uploding single file)
                file.save(os.path.join(app.config["UPLOAD_PATH"],file.filename))
                filename=str(file.filename)
                refer=db.reference("books")
                refer.child(book_name).set({
                        "filename":filename,
                        "about":about,
                        "user_name":session["user"]
                })
            flash(f"Uploaded Successfully',{file.filename}")
            return redirect(url_for('books'))

        else:
            # return "not uploaded"
            return redirect(url_for('books'))
    return redirect(url_for('home'))
@app.route("/download")
def download():
    if 'user' in session:
        return redirect(url_for("login"))

    flash("Login to download this book")
    return redirect(url_for("login"))
if __name__=="__main__":
    app.run(debug=True)
