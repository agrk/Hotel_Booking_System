from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,DateField
from passlib.hash import sha256_crypt
from functools import wraps




app = Flask(__name__, template_folder='templates')

app.secret_key="hotelres"

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_UNIX_SOCKET"] = "/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock"

app.config["MYSQL_DB"]="hotelreservation"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("logn"))

    return decorated_function



#kullanıcı kayıt formu
class RegisterForm(Form):
    Fname=StringField("İsim",validators=[validators.Length(min=4,max=25)])
    Lname=StringField("Soysim",validators=[validators.Length(min=4,max=25)])
    Email=StringField("E-mail Adresi",validators=[validators.Email("Lütfen geçerli bir E-mail adresi giriniz")])
    Username=StringField("Kullanıcı Adı",validators=[validators.Length(min=5,max=35)])
    Password=PasswordField("Parola" ,validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname="Confirm",message="Parolanız Uyuşmuyor")
    ])
    Confirm=PasswordField("Parola Doğrula")
#rezervasyon dbsi
class ReservationForm(Form):
    roomTipi = StringField()
    Destination = StringField()
    
    CheckIn = DateField()
    CheckOut = DateField()
    Yetiskin = StringField()
    Cocuk = StringField()


#login db
class LoginForm(Form):
    Username=StringField("Kullanıcı Adı")
    Password=PasswordField("Parola")

#iletişim dbsi için ----
class ContactForm(Form):
    Name = StringField()
    Email = StringField()
    Phone = StringField()
    Messages = StringField()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/contact" , methods = ["GET", "POST"])
def contact():
    form = ContactForm(request.form)
    if request.method == "POST" and form.validate():
        Name = form.Name.data
        Email = form.Email.data
        Phone = form.Phone.data
        Messages = form.Messages.data
        cursor = mysql.connection.cursor()
        sorgu = "Insert into contact (Name, Email , Phone , Messages ) VALUES (%s,%s,%s,%s)"
        cursor.execute(sorgu,(Name,Email,Phone,Messages))
        mysql.connection.commit()

        cursor.close()
        flash("Mesajınız başarıyla iletildi.","success")
        return redirect(url_for("index"))

    else: 
        return render_template("contact.html", form=form)

@app.route("/reservation",methods=["GET","POST"])
@login_required
def reservation():
   
   
    form = ReservationForm(request.form)
    if request.method=="POST" and form.validate():
        roomTipi = form.roomTipi.data
        Destination = form.Destionation.data
        
        CheckIn = form.CheckIn.data
        CheckOut = form.CheckOut.data
        Yetiskin = form.Yetiskin.data
        Cocuk = form.Cocuk.data
        
        cursor = mysql.connection.cursor()
        sorgu = "Insert into rezerve (guestID,  roomTipi , Destination, CheckIn , CheckOut , Yetiskin , Cocuk  ) VALUES (%s,%s,%s,%s ,%s ,%s , %s)"
        cursor.execute(sorgu,(session["LoginID"],  roomTipi ,Destination, CheckIn , CheckOut , Yetiskin , Cocuk ))
        mysql.connection.commit()

        cursor.close()
        
        return redirect(url_for("index"))

    else: 
        return render_template("reservation.html", form=form)

    


@app.route("/logout",methods=["GET","POST"])
def logout():
    flash("Başarıyla çıkış yapıldı" , "success")
    session.clear()
    
    return redirect(url_for("index"))
 




@app.route("/signup",methods=["GET","POST"])
def signup():
    form=RegisterForm(request.form)

    if request.method=="POST" and form.validate():
        Fname=form.Fname.data
        Lname=form.Lname.data
        Email=form.Email.data
        Username=form.Username.data
        Password= sha256_crypt.encrypt(form.Password.data)


        cursor=mysql.connection.cursor()

        sorgu="Insert into guests (Fname,Lname,Email,Username,Password) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sorgu,(Fname,Lname,Email,Username,Password))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla Kayıt Oldunuz.","success")
        return redirect(url_for("logn"))

    else: 
        return render_template("signup.html", form=form)


@app.route("/logn",methods=["GET","POST"])
def logn(): 

    form=LoginForm(request.form)
    if request.method=="POST":
        Username=form.Username.data
        Password_entered=form.Password.data

        cursor=mysql.connection.cursor()

        sorgu="Select * From guests where Username= %s"

        result=cursor.execute(sorgu,(Username,))

        if result>0:
            data=cursor.fetchone()
            real_password=data["Password"]
            if sha256_crypt.verify(Password_entered,real_password):
                flash("Başarıyla Giriş Yaptınız..","success")
            
                session["logged_in"]=True
                session["Username"]=Username

                return redirect(url_for("index"))
            else:
                flash("Parola Yanlış!","danger")
                return redirect(url_for("logn"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor.","danger")
            return redirect(url_for("signup"))


    return render_template("logn.html",form=form)

if __name__ == "__main__":
    app.run(debug=True)