from flask import *
import pymysql
import sms



# initialise an app
app = Flask(__name__)
# the secret helps you secure your session just incase of an attack
app.secret_key = "tsbtsrvartdyraa5txdfz"


# home route
@app.route("/")
def home():
    # connect to the database
    connection = pymysql.connect(host= "localhost", user="root", password="", database="hillerska")
    # an sql to fetch data
    sql = "SELECT * FROM products WHERE product_category = 'Smartphones' "
    # create a cursor to execute the query
    cursor = connection.cursor()
    # use the cursor to execute the query
    cursor.execute(sql)
    # create a variable that will store all the records fetched from the database
    smartphones = cursor.fetchall()

    # sql to fetch clothes
    sql2 = "SELECT * FROM products WHERE product_category = 'Clothes' "
    cursor.execute(sql2)
    clothes = cursor.fetchall()

    return  render_template("home.html", smartphones = smartphones, clothes=clothes)

# upload Route
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        product_name = request.form["product_name"]
        product_desc = request.form["product_desc"]
        product_cost = request.form["product_cost"]
        product_category = request.form["product_category"]
        product_image_name = request.files["product_image_name"]
        product_image_name.save("static/images/" + product_image_name.filename)

        # create a connection to the database
        connection = pymysql.connect(host="localhost", user="root", password="", database="hillerska")
        # sql to ionsert data to the database. the %s is a placeholder, to be replace with actual data when we execute the sql
        sql = "insert into products(product_name, product_desc, product_cost, product_category, product_image_name) values (%s, %s, %s,%s,%s)"
        # create a variable data that will be used to store the data received from the form
        data = (product_name, product_desc, product_cost, product_category,product_image_name.filename)
        # create a cursor that will be used to execute the query
        cursor = connection.cursor()
        # use the cursor to execute the query
        cursor.execute(sql, data)
        # to finish the insert process we use the commit function
        connection.commit()
        return render_template("upload.html", success = "Uploaded Successfully")
    


@app.route("/single_item/<product_id>")
def single_item(product_id):
    # create a database connection
    connection = pymysql.connect(host="localhost", user="root", password="", database="hillerska")
    # an sql query to fetch one entry/record. the %s is a placeholder to be replaced with actual data when we execute the sql
    sql = "SELECT * FROM `products` WHERE product_id = %s"
    # create a cursor below to help you run/execute the sql
    cursor = connection.cursor()
    # you execute the sql by use of the cursor
    cursor.execute(sql, (product_id))
    # create a varible that will store the record of a single product fetched from the database
    product = cursor.fetchone()
    return render_template("single_item.html", product = product)

@app.route("/register", methods=[ "GET","POST"]) 
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        email = request.form["email"]
        phone = request.form["phone"]

        if password1 != password2:
            return render_template("register.html", error="Password must be the same")
        elif len(password1) < 8:
            return render_template("register.html", error="Password Length must be more than 8 characters")
        else:
            # create a databse connection
            connection = pymysql.connect(host="localhost", user="root", password="", database="hillerska")
            # create an sql to insert the data
            sql = "insert into users(username, password,email, phone) values(%s, %s, %s, %s)"
            # create a variable that will hold the details gotten/picked from the form
            data = (username, password1,email,phone)
            # create a cursor
            cursor = connection.cursor()
            # use the cursor to execute the sql
            cursor.execute(sql, data)
            # finish the transaction of inserting by use of the commit function
            connection.commit()

            # sennding an sms after a successful registrationm
            sms.send_sms(phone, f"{username} Thank you for registering. Welcome to sokogarden")
            return render_template("register.html", success="User Registered successfully")
        

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # get the details entered on the form and store them in a variable
        username = request.form["username"]
        password = request.form["password"]
        # create a db connection
        connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenb")
        # create an sql query. The %s is a placeholder, to be replaced with actual data when we execute the sql
        sql = "SELECT * FROM `users` WHERE username = %s and password=%s"
        # create a varible that will hold the data gotten from the form
        data = (username, password)
        # create a cursor that will help to execute the sql
        cursor = connection.cursor()
        # execute the query
        cursor.execute(sql, data)

        # fetch one person
        user = cursor.fetchone()

        if cursor.rowcount== 0:
            return render_template("login.html", error="Invalid Credentials")
        else:
            session["key"] = username
            session["profile_picture"] = user[6]
            return redirect("/")
        

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")

@app.route("/user")
def user():
    
        # create a db connection
        connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenb")
        # create an sql query. The %s is a placeholder, to be replaced with actual data when we execute the sql
        sql = "SELECT * FROM `users`"
        # create a cursor that will help to execute the sql
        cursor = connection.cursor()
        # execute the query
        cursor.execute(sql)

        # fetch one person
        user = cursor.fetchall()
        return render_template("userupdate.html", user=user)


@app.route("/delete/<username>", methods=["POST"])
def delete_user(username):
    connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenb")
    cursor = connection.cursor()

    # SQL to delete the user by username
    sql = "DELETE FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    connection.commit()
    
    return redirect("/user")  # Redirect back to the user list after deletion

@app.route("/update/<username>", methods=["GET", "POST"])
def update_user(username):
    connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenb")
    cursor = connection.cursor()

    if request.method == "POST":
        # Get updated data from form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        profile_picture = request.form.get('profile_picture')

        # Update the user details in the database
        sql = """
        UPDATE users 
        SET first_name = %s, last_name = %s, password = %s, email = %s, phone_number = %s, profile_picture = %s 
        WHERE username = %s
        """
        cursor.execute(sql, (first_name, last_name, password, email, phone_number, profile_picture, username))
        connection.commit()

        return redirect("/user")  # Redirect to the users list

    # For GET, we display the current user data to be updated
    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    return render_template("user_update_form.html", user=user)


# the imports for the mpesa function
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/mpesapayment', methods=['POST', 'GET'])
def mpesa_payment():
    if request.method == 'POST':
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # GENERATING THE ACCESS TOKEN
        # create an account on safaricom daraja
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return '<h3>Please Complete Payment in Your Phone and we will deliver in minutes</h3>' \
               '<a href='"/"' class="btn btn-dark btn-sm">Back to Products</a>'



            
app.run(debug=True)
# end of the server