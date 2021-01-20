import sqlite3, psycopg2
import flask
import json
from flask import jsonify, request, render_template,redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
import hashlib
import os
import psycopg2 as dpapi

#url = os.getenv("DB_URL")
url = "dbname='wezrrgcd' user='wezrrgcd' host='salt.db.elephantsql.com' password='gh4WaN_uVpfMTkAMF3AG-h2nXbbNr1FH' "

app = flask.Flask(__name__,template_folder="templates")
app.secret_key = "sdsgchg"
ingreList = [];
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'static/assets/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    print("filename",filename)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    cursor.execute("""SELECT comment.commentid, comment.title, comment.usercomment, comment.commentdate, comment.commentlike, f.foodid, f.foodname, f.foodphoto, m.username FROM comment 
                          JOIN food f ON comment.foodid = f.foodid JOIN members m on comment.memberid = m.memberid  ORDER BY comment.commentlike DESC NULLS LAST LIMIT 2     
                        """)
    data = cursor.fetchall()

    cursor.execute("""SELECT comment.commentid, comment.title, comment.usercomment, comment.commentdate, comment.commentlike, d.dessertid, d.dessertname, d.dessertphoto, m.username FROM comment 
                          JOIN dessert d ON comment.dessertid = d.dessertid JOIN members m on comment.memberid = m.memberid ORDER BY comment.commentlike DESC NULLS LAST """)
    data2 = cursor.fetchone()

    cursor.execute("""SELECT comment.commentid, comment.title, comment.usercomment, comment.commentdate, comment.commentlike, b.beverageid, b.beveragename, b.beveragephoto, m.username FROM comment 
                              JOIN beverage b ON comment.beverageid = b.beverageid JOIN members m on comment.memberid = m.memberid ORDER BY comment.commentlike DESC NULLS LAST """)
    data3 = cursor.fetchone()

    cursor.execute("""SELECT  food.foodid, food.foodname, food.foodrecipe, food.foodphoto, food.fooddate FROM food 
                            ORDER BY food.fooddate DESC NULLS LAST """)
    data4 = cursor.fetchone()

    cursor.execute("""SELECT  dessert.dessertid, dessert.dessertname, dessert.dessertrecipe, dessert.dessertphoto, dessert.dessertdate FROM dessert 
                                ORDER BY dessert.dessertdate DESC NULLS LAST """)
    data5 = cursor.fetchone()

    cursor.execute("""SELECT  beverage.beverageid, beverage.beveragename, beverage.beveragerecipe, beverage.beveragephoto, beverage.beveragedate FROM beverage 
                                ORDER BY beverage.beveragedate DESC NULLS LAST """)
    data6 = cursor.fetchone()

   # cursor.execute("SELECT food.foodid, food.foodname, food.foodrecipe, food.foodphoto, food.foodtype, food.foodscore FROM food ORDER BY foodscore ASC LIMIT 1")
   # data2 = cursor.fetchall()

    username = ""
    if 'username' in session:
        username = session['username']

    if data or data2 or data3 or data4 or data5 or data6:
        conn.close()
        return render_template("index.html", comment1 =data, len=len(data), comment2=data2, comment3=data3, beverage=data6, food= data4, dessert= data5, username=username)
    else:
        conn.close()
        return render_template("index.html", username=username)



@app.route('/profile', methods=['GET' , 'POST'])
def profile():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    if "id" in session:
        cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username, personaldata.personalid FROM members 
                       INNER JOIN personaldata 
                       ON personaldata.memberid = members.memberid and members.memberid=%s;""", (session["id"],))
        data = cursor.fetchall()

        cursor.execute(""" SELECT food.foodid, food.foodphoto, food.foodname, qualification.cuisine, qualification.timing, qualification.qualificationid, food.foodrecipe FROM qualification
                    INNER JOIN food
                    ON food.qualificationid = qualification.qualificationid and food.memberid = %s;""",(session["id"],))

        foods = cursor.fetchall()

        cursor.execute(""" SELECT dessert.dessertid, dessert.dessertphoto, dessert.dessertname, qualification.cuisine, qualification.timing, qualification.qualificationid, dessert.dessertrecipe FROM qualification
                        INNER JOIN dessert
                        ON dessert.qualificationid = qualification.qualificationid and dessert.memberid = %s;""",(session["id"],))

        desserts = cursor.fetchall()

        cursor.execute(""" SELECT beverage.beverageid, beverage.beveragephoto, beverage.beveragename, qualification.cuisine, qualification.timing, qualification.qualificationid, beverage.beveragerecipe FROM qualification
                        INNER JOIN beverage
                        ON beverage.qualificationid = qualification.qualificationid and beverage.memberid = %s;""", (session["id"],))

        drinks = cursor.fetchall()

        if request.method == 'POST':

            deletedrink = request.form.get('drinkdelete')
            deletedessert = request.form.get('dessertdelete')
            deletefood = request.form.get('fooddelete')

            if deletedrink:
                i = 0

                while i < len(drinks):
                    deletedrink = drinks[i][0]
                    qid = drinks[i][5]
                    cursor.execute(""" DELETE FROM comment WHERE comment.beverageid=%s""", (str(deletedrink),))
                    cursor.execute( """ DELETE FROM ingredient WHERE ingredient.beverageid IN (SELECT beverageid FROM beverage WHERE beverage.beverageid = %s)""", (str(deletedrink),))
                    cursor.execute(""" DELETE FROM beverage WHERE beverage.beverageid= %s""", (str(deletedrink),))
                    cursor.execute(""" DELETE FROM qualification WHERE qualification.qualificationid=%s """,
                                   (str(qid),))
                    conn.commit()
                    i = i + 1
                conn.close()
                return redirect(url_for('profile'))

            elif deletefood:
                i = 0

                while i < len(foods):
                    deletefood = foods[i][0]
                    qid = foods[i][5]
                    cursor.execute(""" DELETE FROM comment WHERE comment.foodid=%s""", (str(deletefood),))
                    cursor.execute( """ DELETE FROM ingredient WHERE ingredient.foodid IN (SELECT foodid FROM food WHERE food.foodid = %s)""",  (str(deletefood),))
                    cursor.execute(""" DELETE FROM food WHERE food.foodid= %s""", (str(deletefood),))
                    cursor.execute(""" DELETE FROM qualification WHERE qualification.qualificationid=%s """,
                                   (str(qid),))
                    conn.commit()
                    i = i + 1
                conn.close()
                return redirect(url_for('profile'))

            elif deletedessert:
                i = 0

                while i < len(desserts):

                    deletedessert = desserts[i][0]
                    print(desserts[i][0])

                    qid = desserts[i][5]
                    cursor.execute(""" DELETE FROM comment WHERE comment.dessertid=%s""",  (str(deletedessert),))
                    cursor.execute( """ DELETE FROM ingredient WHERE ingredient.dessertid IN (SELECT dessertid FROM dessert WHERE dessert.dessertid = %s)""", (str(deletedessert),))
                    cursor.execute(""" DELETE FROM dessert WHERE dessert.dessertid= %s""", (str(deletedessert),))
                    cursor.execute(""" DELETE FROM qualification WHERE qualification.qualificationid=%s """, (str(qid),))
                    conn.commit()
                    i = i + 1
                conn.close()
                return redirect(url_for('profile'))
            else:
                i=0
                while i < len(foods):
                    foodid = foods[i][0]
                    qid = foods[i][5]
                    print(qid, str(foodid))
                    cursor.execute(""" DELETE FROM comment WHERE comment.memberid=%s""", (str(session["id"]),))
                    cursor.execute(""" DELETE FROM ingredient WHERE ingredient.foodid IN (SELECT foodid FROM food WHERE food.memberid = %s)""", (str(session["id"]),))
                    cursor.execute(""" DELETE FROM food WHERE food.foodid= %s""", (str(foodid),))
                    cursor.execute(""" DELETE FROM qualification WHERE qualification.qualificationid=%s """, (str(qid),))
                    conn.commit()
                    i = i + 1

                i = 0
                while i < len(drinks):
                     drinkid = drinks[i][0]
                     qid = drinks[i][5]
                     cursor.execute(""" DELETE FROM comment WHERE comment.memberid=%s""", (str(session["id"]),))
                     cursor.execute(""" DELETE FROM ingredient WHERE ingredient.beverageid IN (SELECT beverageid FROM beverage WHERE beverage.memberid = %s)""",(str(session["id"]),))
                     cursor.execute(""" DELETE FROM beverage WHERE beverage.beverageid= %s""", (str(drinkid),))
                     cursor.execute(""" DELETE FROM qualification WHERE qualification.qualificationid=%s """, (str(qid),))
                     conn.commit()
                     i = i + 1

                i = 0
                while i < len(desserts):
                     dessertid = desserts[i][0]
                     qid = desserts[i][5]
                     cursor.execute(""" DELETE FROM comment WHERE comment.memberid= %s""", (str(session["id"]),))
                     cursor.execute(""" DELETE FROM ingredient WHERE ingredient.dessertid IN (SELECT dessertid FROM dessert WHERE dessert.memberid = %s)""",(str(session["id"]),))
                     cursor.execute(""" DELETE FROM dessert WHERE dessert.dessertid= %s""", (str(dessertid),))
                     cursor.execute(""" DELETE FROM qualification WHERE qualification.qualificationid=%s """, (str(qid),))
                     conn.commit()
                     i = i + 1


                cursor.execute(""" DELETE FROM personaldata WHERE memberid= %s""", (str(session["id"]),))
                cursor.execute(""" DELETE FROM members WHERE memberid= %s""", (str(session["id"]),))
                conn.commit()

                if 'id' in session:
                    session.pop('id')
                if 'username' in session:
                    session.pop('username')

                conn.close()
                return redirect(url_for('home'))

        if data or foods or drinks or desserts:
            conn.close()
            return render_template("profile.html", authority=session["authority"] , datam=data, foodlen =len(foods), drinklen =len(drinks), dessertlen=len(desserts), food=foods, dessert=desserts, drink=drinks)
        else:
            conn.close()
            return render_template("profile.html" , datam=data, authority=session["authority"]  ,foodlen =len(foods),drinklen =len(drinks), dessertlen=len(desserts), food=foods, dessert=desserts, drink=drinks)

    conn.close()
    return render_template("index.html")


@app.route('/all-contacts', methods=['GET' , 'POST'])
def all_contacts():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    if request.method == 'POST':
        contactid = request.form.get('contactid')
        statusValue = request.form.get('status')
        print(statusValue)
        if statusValue == 'put':
            cursor.execute("UPDATE contact SET status = %s WHERE contact.contactid = %s",
            (True,contactid,))
        else:
            cursor.execute("DELETE FROM contact WHERE contactid=%s" , (str(contactid),))

        conn.commit()
        conn.close()
        return redirect(url_for('all_contacts', status="done" ))
    else:
        if "authority" in session:
            authority = session['authority']
            cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username FROM members 
                              INNER JOIN personaldata 
                              ON personaldata.memberid = members.memberid and members.memberid = %s """,
                           (str(session["id"]),))
            data = cursor.fetchall()

            if authority == 'admin':
                cursor.execute("SELECT contactid, message, date, title, category, e_mail, status FROM contact")
                contacts = cursor.fetchall()

            if contacts:
                conn.close()
                return render_template("show-contacts.html",authority=session["authority"] , contact=contacts, datam=data, contactlen=len(contacts))
            else:
                conn.close()
                return render_template("show-contacts.html",authority=session["authority"] ,  datam=data, contactlen=0, result="No contact..")
        else :
            conn.close()
            return render_template(url_for("profile"))

@app.route('/change-info', methods=['GET' , 'POST'])
def changeInfo():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    firstname = request.form.get("FirstName")
    lastname = request.form.get("LastName")
    gender = request.form.get("Gender")
    birthdate = request.form.get("Birthdate")
    location = request.form.get("Location")
    email = request.form.get("email")
    password = request.form.get("password")

    cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username,  members.userpassword FROM members 
                                    INNER JOIN personaldata 
                                    ON personaldata.memberid = members.memberid and members.memberid = %s """, (str(session["id"]),))
    data2 = cursor.fetchall()
    print(data2)

    if request.method == "POST":
        cursor.execute(
            "UPDATE personaldata SET name = %s, surname = %s , birthdate = %s, sex = %s, location = %s  WHERE personaldata.memberid = %s",
            (firstname, lastname, birthdate, gender, location, session["id"]))
        cursor.execute(
            "UPDATE members SET e_mail = %s, userpassword = %s WHERE members.memberid = %s",
            (email, hashlib.md5(password.encode('utf-8')).hexdigest(), session["id"]))
        conn.commit()
        conn.close()
        return redirect(url_for('profile', authority=session["authority"] , datam=data2))

    else:
        cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.sex, personaldata.birthdate, personaldata.location, members.userpassword FROM personaldata 
                            INNER JOIN members 
                            ON personaldata.memberid = members.memberid and members.memberid = %s """,(str(session["id"]),))
        data = cursor.fetchall()
        print(data)
        conn.close()
        return render_template('change-info.html',  authority=session["authority"] , info=data, datam=data2)


@app.route('/sign-in', methods=['GET'])
def get_members():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    userName = request.args.get("username")
    passWord = request.args.get("password")

    if userName and passWord:
        print(hashlib.md5(passWord.encode('utf-8')).hexdigest())
        if request.form.get("forgotPassword"):
            return render_template("index.html")
        cursor.execute("SELECT * FROM members where username=%s and userpassword=%s",(userName,hashlib.md5(passWord.encode('utf-8')).hexdigest()))
        data = cursor.fetchone()
        conn.commit()
        if data:
            session["username"]= userName
            session["id"] = data[0]
            session['authority'] = data[6]
            conn.close()
            return redirect(url_for('home', username=session["username"]))
        else:
            myerror="Please try again!"
            conn.close()
            return render_template('login-page.html', errors=myerror)
    else :
        conn.close()
        return render_template("login-page.html")


@app.route('/logout', methods=['GET'])
def logout():
   conn = dpapi.connect(url)
   cursor = conn.cursor()

   if 'id' in session:
        session.pop('id')
   if 'username' in session:
        session.pop('username')

   conn.close()
   return redirect(url_for('home'))


@app.route('/new-password', methods=['GET'])
def newPass():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    userName = request.args.get("username")
    e_mail = request.args.get("email")
    answer = request.args.get("answer")
    newpassword = request.args.get("password")


    cursor.execute("SELECT recoveryques, recoveryans, memberid FROM members where username=%s and e_mail=%s",(userName,e_mail))
    data = cursor.fetchone()


    if data:
        session['memberid'] = data[2]
        print(data[2])
        conn.close()
        return render_template('new-password.html', email=e_mail, datam=data)

    if answer:
        data = 'a'
        memberid = session['memberid']
        print("aa",memberid)
        conn.close()
        return render_template('new-password.html', datam=data, ans=answer, memberid=memberid)

    if newpassword:
        memberid = session['memberid']
        print("bb",memberid)
        cursor.execute("UPDATE members SET userpassword = %s  WHERE members.memberid = %s", (hashlib.md5(newpassword.encode('utf-8')).hexdigest(), memberid))
        conn.commit()
        conn.close()
        return redirect(url_for('profile', id=id))

    conn.close()
    return render_template('new-password.html')



@app.route('/sign-up', methods=['GET','POST'])
def signUp():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    if 'id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        firstname = request.form.get("FirstName")
        lastname = request.form.get("LastName")
        email = request.form.get("Email")
        username = request.form.get("Username")
        password = request.form.get("Password")
        gender = request.form.get("Gender")
        birthdate = request.form.get("Birthdate")
        location = request.form.get("Location")
        rques = request.form.get("RecoveryQuestion")
        ranswer = request.form.get("RecoveryAnswer")

        if firstname and lastname and email and username and password and gender and birthdate and location and rques and ranswer:
            cursor.execute("INSERT INTO members(username, userpassword, e_mail, recoveryques, recoveryans, authority) VALUES (%s, %s, %s, %s, %s, %s) RETURNING memberid",(username, hashlib.md5(password.encode('utf-8')).hexdigest(), email, rques, ranswer, 'user'))
            conn.commit()
            sql=cursor.fetchone()[0]
            cursor.execute("INSERT INTO personaldata (name, surname, birthdate, sex, location, memberid) "
                             "VALUES (%s,%s,%s,%s,%s,%s)", (firstname, lastname, birthdate, gender, location, sql))
            conn.commit()

            session["username"] = username
            session["id"] = sql
            session['authority'] = 'user'
            conn.close()
            return redirect(url_for('home', username=session["username"]))
        
    elif request.method == 'GET':
        conn.close()
        return render_template("sign-page.html")




@app.route('/food-menu', methods=['GET'])
def foods():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    cursor.execute("""
                SELECT food.foodid, food.foodphoto, food.foodname, qualification.cuisine, qualification.timing, qualification.qualificationid  FROM qualification
                INNER JOIN food
                ON food.qualificationid = qualification.qualificationid""")

    data = cursor.fetchall()
    username = ""
    if 'username' in session:
        username = session['username']
    if data:
        conn.close()
        return render_template("food-menu.html", len = len(data), food=data, username=username)
    else:
        conn.close()
        return render_template("food-menu.html", username=username)


@app.route('/drink-menu', methods=['GET'])
def drinks():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    cursor.execute("""
                SELECT beverage.beverageid, beverage.beveragephoto, beverage.beveragename,  qualification.cuisine,  qualification.timing, qualification.qualificationid FROM qualification
                INNER JOIN beverage
                ON beverage.qualificationid = qualification.qualificationid""")

    data = cursor.fetchall()
    username = ""
    if 'username' in session:
        username = session['username']
    if data:
        conn.close()
        return render_template("drink-menu.html", len=len(data), drink=data, username=username)
    else:
        conn.close()
        return render_template("drink-menu.html", username=username)


@app.route('/dessert-menu', methods=['GET'])
def desserts():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    cursor.execute("""
                SELECT dessert.dessertid,  dessert.dessertphoto, dessert.dessertname, qualification.cuisine, qualification.timing, qualification.qualificationid FROM qualification
                INNER JOIN dessert
                ON dessert.qualificationid = qualification.qualificationid""")

    data = cursor.fetchall()
    username = ""
    if 'username' in session:
        username = session['username']
    if data:
        conn.close()
        return render_template("dessert-menu.html", len=len(data), dessert=data, username=username)
    else:
        conn.close()
        return render_template("dessert-menu.html", username=username)


@app.route('/recipe/food/<id>', methods=['GET', 'POST'])
def foodRecipe(id):

    conn = dpapi.connect(url)
    cursor = conn.cursor()
    if request.method == 'POST':
        mytitle = request.form.get("title")
        mycomment = request.form.get("comment")
        like = request.form.get("like")
        dislike = request.form.get("dislike")
        comment_id = request.form.get("commentid")
        date = request.form.get("commentdate")

        print(comment_id)
        if like == "PUT":
            cursor.execute("UPDATE comment SET commentlike = commentlike + 1 WHERE comment.foodid = %s and comment.commentid = %s ", (id,comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('foodRecipe', id=id))

        elif dislike == "PUT":
            cursor.execute("UPDATE comment SET commentdislike = commentdislike + 1 WHERE comment.foodid = %s and comment.commentid = %s ", (id,comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('foodRecipe', id=id))

        if mycomment and mytitle:
            cursor.execute("INSERT INTO comment(usercomment, title, foodid, memberid, commentdate) VALUES (%s, %s, %s, %s, %s)",
                           (mycomment, mytitle, id, str(session["id"]), date))
            conn.commit()
            conn.close()
            return redirect(url_for('foodRecipe', id=id))
    else:
        cursor.execute("""
                    SELECT food.foodid, food.foodname, food.foodphoto, food.foodrecipe, ingredient.ingrename, ingredient.unit, ingredient.amount, qualification.cuisine, qualification.qualificationid, qualification.timing, food.fooddate, qualification.calori, qualification.serve, qualification.category, food.memberid, food.foodtype FROM food
                    INNER JOIN qualification
                    ON food.qualificationid = qualification.qualificationid
                    INNER JOIN  ingredient
                    ON ingredient.foodid = food.foodid AND food.foodid = %s""", (id,))
        data = cursor.fetchone()
        foodid = data[0]
        memberid=data[14]
        cursor.execute("SELECT comment.usercomment, comment.commentdate, members.username, comment.title, comment.commentlike, comment.commentdislike, comment.commentid FROM comment INNER JOIN members ON comment.memberid = members.memberid where comment.foodid = %s ", (foodid,))
        data2 = cursor.fetchall()

        cursor.execute("SELECT ingredient.ingrename, ingredient.unit, ingredient.amount, ingredient.allergenic FROM ingredient INNER JOIN food ON ingredient.foodid = food.foodid AND food.foodid = %s """,(id,))
        data3 = cursor.fetchall()

        cursor.execute("SELECT username FROM members where memberid=%s",(memberid,))
        foodusername = cursor.fetchone()
        username = ""
        if 'username' in session:
            username = session['username']
        if data:
            conn.close()
            return render_template("recipe.html", len=len(data2), len2=len(data3), datam=data , fooduser=foodusername ,comment=data2, ingre=data3, username=username)

    conn.close()
    return render_template("recipe.html")


@app.route('/recipe/drink/<id>', methods=['GET', 'POST'])
def drinkRecipe(id):
    conn = dpapi.connect(url)
    cursor = conn.cursor()

    if request.method == 'POST':
        mytitle = request.form.get("title")
        mycomment = request.form.get("comment")
        like = request.form.get("like")
        dislike = request.form.get("dislike")
        comment_id = request.form.get("commentid")
        date = request.form.get("commentdate")

        print(comment_id)
        if like == "PUT":
            cursor.execute(
                "UPDATE comment SET commentlike = commentlike + 1 WHERE comment.beverageid = %s and comment.commentid = %s ",
                (id, comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('drinkRecipe', id=id))

        elif dislike == "PUT":
            cursor.execute(
                "UPDATE comment SET commentdislike = commentdislike + 1 WHERE comment.beverageid = %s and comment.commentid = %s ",
                (id, comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('drinkRecipe', id=id))

        if mycomment and mytitle:
            cursor.execute("INSERT INTO comment(usercomment, title, beverageid, memberid, commentdate) VALUES (%s, %s, %s, %s, %s)",
                           (mycomment, mytitle, id,  str(session["id"]), date))
            conn.commit()
            conn.close()
            return redirect(url_for('drinkRecipe', id=id))
    else:
        cursor.execute("""
                            SELECT beverage.beverageid, beverage.beveragename, beverage.beveragephoto, beverage.beveragerecipe, ingredient.ingrename, ingredient.unit, ingredient.amount, qualification.cuisine, qualification.qualificationid, qualification.timing, beverage.beveragedate, qualification.calori, qualification.serve, qualification.category, beverage.memberid, beverage.beveragetype FROM beverage
                            INNER JOIN qualification
                            ON beverage.qualificationid = qualification.qualificationid
                            INNER JOIN  ingredient
                            ON ingredient.beverageid = beverage.beverageid AND beverage.beverageid = %s""", (id,))
        data = cursor.fetchone()
        drinkid = data[0]
        memberid = data[14]
        cursor.execute(
            "SELECT comment.usercomment, comment.commentdate, members.username, comment.title, comment.commentlike, comment.commentdislike, comment.commentid  FROM comment INNER JOIN members ON comment.memberid = members.memberid where comment.beverageid = %s ",
            (drinkid,))
        data2 = cursor.fetchall()

        cursor.execute(
            "SELECT ingredient.ingrename, ingredient.unit, ingredient.amount, ingredient.allergenic FROM ingredient INNER JOIN beverage ON ingredient.beverageid = beverage.beverageid AND beverage.beverageid = %s """,
            (id,))
        data3 = cursor.fetchall()

        cursor.execute("SELECT username FROM members where memberid=%s", (memberid,))
        beverageuser = cursor.fetchone()

        username = ""
        if 'username' in session:
            username = session['username']

        if data:
            conn.close()
            return render_template("recipe.html", len=len(data2), len2=len(data3), datam=data, fooduser=beverageuser ,comment=data2, ingre=data3, username=username)

    conn.close()
    return render_template("recipe.html")



@app.route('/recipe/dessert/<id>', methods=['GET', 'POST'])
def dessertRecipe(id):
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    print(session)
    if request.method == 'POST':
        mytitle = request.form.get("title")
        mycomment = request.form.get("comment")
        like = request.form.get("like")
        dislike = request.form.get("dislike")
        comment_id = request.form.get("commentid")
        date = request.form.get("commentdate")
        print(date)

        if like == "PUT":
            cursor.execute(
                "UPDATE comment SET commentlike = commentlike + 1 WHERE comment.dessertid = %s and comment.commentid = %s ",
                (id, comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('dessertRecipe', id=id))

        elif dislike == "PUT":
            cursor.execute(
                "UPDATE comment SET commentdislike = commentdislike + 1 WHERE comment.dessertid = %s and comment.commentid = %s ",
                (id, comment_id))
            conn.commit()
            conn.close()
            return redirect(url_for('dessertRecipe', id=id))

        if mycomment and mytitle:
            cursor.execute("INSERT INTO comment(usercomment, title, dessertid, memberid, commentdate) VALUES (%s, %s, %s, %s, %s)",
                           (mycomment, mytitle, id,  str(session["id"]), date))
            conn.commit()
            conn.close()
            return redirect(url_for('dessertRecipe', id=id))
    else:
        cursor.execute("""
                            SELECT dessert.dessertid, dessert.dessertname, dessert.dessertphoto, dessert.dessertrecipe, ingredient.ingrename, ingredient.unit, ingredient.amount, qualification.cuisine, qualification.qualificationid, qualification.timing, dessert.dessertdate, qualification.calori, qualification.serve, qualification.category, dessert.memberid, dessert.desserttype FROM dessert
                            INNER JOIN qualification
                            ON dessert.qualificationid = qualification.qualificationid
                            INNER JOIN  ingredient
                            ON dessert.dessertid = dessert.dessertid AND dessert.dessertid = %s""", (id,))
        data = cursor.fetchone()
        dessertid = data[0]
        memberid = data[14]
        cursor.execute(
            "SELECT comment.usercomment, comment.commentdate, members.username, comment.title, comment.commentlike, comment.commentdislike, comment.commentid FROM comment INNER JOIN members ON comment.memberid = members.memberid where comment.dessertid = %s ",
            (dessertid,))
        data2 = cursor.fetchall()

        cursor.execute(
            "SELECT ingredient.ingrename, ingredient.unit, ingredient.amount, ingredient.allergenic FROM ingredient INNER JOIN dessert ON ingredient.dessertid = dessert.dessertid AND dessert.dessertid = %s """,
            (id,))
        data3 = cursor.fetchall()

        cursor.execute("SELECT username FROM members where memberid=%s", (memberid,))
        dessertuser = cursor.fetchone()

        username = ""
        if 'username' in session:
            username = session['username']
        if data:
            conn.close()
            return render_template("recipe.html", len=len(data2), len2=len(data3), datam=data, fooduser=dessertuser ,comment=data2, ingre=data3, username=username)

    conn.close()
    return render_template("recipe.html")


@app.route('/add-recipe', methods=['GET','POST'])
def post_food():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    qualificationId = 0
    if request.method == 'POST':
        memberid = session["id"]
        name = request.form.get('recipename')
        time = request.form.get('recipetime')
        calorie = request.form.get('recipecalorie')
        country = request.form.get('recipecountry')
        type = request.form.get('recipetype')
        date = request.form.get('recipedate')
        serve = request.form.get('recipeserve')
        recipe = request.form.get('recipes')
        category = request.form.get('recipecategory')
        photo = request.form.get('recipephoto')
        recipeType = request.form.get('recipeType')
        print(name , time , calorie, date , country, serve , recipe)

        if name and time and calorie and date and serve and recipe:
            print("Asdfsdf")
            cursor.execute("INSERT INTO qualification(cuisine, timing, category, calori, serve) VALUES(%s,%s,%s,%s,%s) RETURNING qualificationid",
                              (country, time, category, calorie, serve))
            qualificationId = cursor.fetchone()[0]
            conn.commit()

            id=0
            if recipeType == "food":
                cursor.execute("INSERT INTO food(foodname, foodrecipe, foodphoto, foodtype, qualificationid, memberid, fooddate) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING foodid" ,
                            (name, recipe, photo, type, qualificationId, memberid, date))
                id = cursor.fetchone()[0]
                print("food", id)
                conn.commit()
            elif recipeType == "beverage":
                cursor.execute(
                    "INSERT INTO beverage(beveragename, beveragerecipe, beveragephoto, beveragetype, qualificationid, memberid, beveragedate) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING beverageid",
                    (name, recipe, photo, type, qualificationId, memberid, date))
                id = cursor.fetchone()[0]
                print("beverage", id)
                conn.commit()
            elif recipeType == "dessert":
                cursor.execute(
                    "INSERT INTO dessert(dessertname, dessertrecipe, dessertphoto, desserttype, qualificationid, memberid, dessertdate) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING dessertid",
                    (name, recipe, photo, type, qualificationId, memberid, date))
                id = cursor.fetchone()[0]
                print("dessert", id)
                conn.commit()

            i = 0
            while request.form.get("ingrename" + str(i)) :
                ingreFlavor = ""
                ingreallergenic = False
                ingrename = request.form.get("ingrename" + str(i))
                ingreamount = request.form.get("ingreamount" + str(i))
                ingreunit = request.form.get("ingreunit" + str(i))
                if request.form.get("ingreallegernic" + str(i)):
                    ingreallergenic = True
                if request.form.get("flavorHot" + str(i)):
                    ingreFlavor = ingreFlavor + "Hot"
                if request.form.get("flavorSweet" + str(i)):
                    ingreFlavor = ingreFlavor + ",Sweet"
                if request.form.get("flavorSour" + str(i)):
                    ingreFlavor = ingreFlavor + ",Sour"
                if recipeType == "food":
                    cursor.execute("INSERT INTO ingredient(ingrename, unit, amount, allergenic, flavor, foodid) VALUES (%s,%s,%s,%s,%s,%s)",
                        (ingrename, ingreunit, ingreamount, ingreallergenic, ingreFlavor, id))
                elif recipeType == "beverage":
                    cursor.execute(
                        "INSERT INTO ingredient(ingrename, unit, amount, allergenic, flavor, beverageid) VALUES (%s,%s,%s,%s,%s,%s)",
                        (ingrename, ingreunit, ingreamount, ingreallergenic, ingreFlavor, id))
                elif recipeType == "dessert":
                    cursor.execute(
                        "INSERT INTO ingredient(ingrename, unit, amount, allergenic, flavor, dessertid) VALUES (%s,%s,%s,%s,%s,%s)",
                        (ingrename, ingreunit, ingreamount, ingreallergenic, ingreFlavor, id))
                i = i + 1
                conn.commit()

            cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username FROM members 
                                       INNER JOIN personaldata 
                                       ON personaldata.memberid = members.memberid and members.memberid = %s """,
                           (session["id"],))
            data2 = cursor.fetchall()
            conn.close()
            return redirect(url_for("profile"))
    else:
        if "id" in session:
            print(session["id"])
            cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username FROM members 
                            INNER JOIN personaldata 
                            ON personaldata.memberid = members.memberid and members.memberid = %s """,(session["id"],))
            data = cursor.fetchall()
        conn.close()
        return render_template("add-recipe.html" , datam=data,  authority=session["authority"] )


@app.route('/change-recipe/food/<id>', methods=['GET','POST'])
def change_food(id):
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    qualificationId = 0
    if request.method == 'POST':
        memberid = session["id"]
        qualificationid = request.form.get('qualificationid')
        name = request.form.get('recipename')
        time = request.form.get('recipetime')
        calorie = request.form.get('recipecalorie')
        country = request.form.get('recipecountry')
        type = request.form.get('recipetype')
        date = request.form.get('recipedate')
        serve = request.form.get('recipeserve')
        recipe = request.form.get('recipes')
        category = request.form.get('recipecategory')
        recipeType = request.form.get('recipeType')
        print(name , time , calorie, date , country, serve , recipe)
        cursor.execute("UPDATE qualification SET cuisine = %s , timing = %s, category = %s, calori = %s, serve= %s WHERE qualificationid = %s",
                        (country, time, category, calorie, serve, qualificationid))
        cursor.execute(
            "UPDATE food SET foodname = %s , foodrecipe = %s, foodtype = %s WHERE foodid = %s",
            (name, recipe, type, id))

        i=0
        while request.form.get("ingrename" + str(i)):
            ingreid = request.form.get("ingredientid"+ str(i))
            ingrename = request.form.get("ingrename" + str(i))
            ingreamount = request.form.get("ingreamount" + str(i))
            ingreunit = request.form.get("ingreunit" + str(i))
            print(ingrename,ingreamount,ingreunit)
            cursor.execute(
                "UPDATE ingredient SET ingrename = %s , unit = %s, amount = %s WHERE foodid = %s and ingredientid=%s ",
                (ingrename, ingreunit, ingreamount, id , ingreid))
            conn.commit()
            i=i+1
        conn.commit()
        conn.close()
        return redirect(url_for("profile"))
    else:
        mymemberid = session["id"]
        cursor.execute(""" SELECT food.foodname, qualification.cuisine, qualification.calori, qualification.serve,  qualification.timing, qualification.category,food.foodrecipe, food.foodtype, qualification.qualificationid FROM qualification
                    INNER JOIN food
                    ON food.qualificationid = qualification.qualificationid and food.foodid=%s""", (id,))
        foods = cursor.fetchone()
        print(foods[4])
        cursor.execute("SELECT ingredient.ingrename, ingredient.unit, ingredient.amount, ingredient.ingredientid FROM ingredient INNER JOIN food ON ingredient.foodid = food.foodid AND food.foodid = %s """,(id,))
        data3 = cursor.fetchall()
        print(data3)
        cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username FROM members 
                           INNER JOIN personaldata 
                           ON personaldata.memberid = members.memberid and members.memberid = %s """,(mymemberid,))
        memberdata = cursor.fetchall()
        conn.close()
        return render_template("change-recipe.html",  authority=session["authority"]  ,datam=memberdata, data=foods , ingre=data3 , ingrelen=len(data3))


@app.route('/change-recipe/dessert/<id>', methods=['GET','POST'])
def change_dessert(id):
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    qualificationId = 0
    if request.method == 'POST':
        memberid = session["id"]
        qualificationid = request.form.get('qualificationid')
        name = request.form.get('recipename')
        time = request.form.get('recipetime')
        calorie = request.form.get('recipecalorie')
        country = request.form.get('recipecountry')
        type = request.form.get('recipetype')
        date = request.form.get('recipedate')
        serve = request.form.get('recipeserve')
        recipe = request.form.get('recipes')
        category = request.form.get('recipecategory')
        recipeType = request.form.get('recipeType')
        print(name , time , calorie, date , country, serve , recipe)
        cursor.execute("UPDATE qualification SET cuisine = %s , timing = %s, category = %s, calori = %s, serve= %s WHERE qualificationid = %s",
                        (country, time, category, calorie, serve, qualificationid))
        cursor.execute(
            "UPDATE dessert SET dessertname = %s , dessertrecipe = %s, desserttype = %s WHERE dessertid = %s",
            (name, recipe, type, id))

        i=0
        while request.form.get("ingrename" + str(i)):
            ingreid = request.form.get("ingredientid"+ str(i))
            ingrename = request.form.get("ingrename" + str(i))
            ingreamount = request.form.get("ingreamount" + str(i))
            ingreunit = request.form.get("ingreunit" + str(i))
            print(ingrename,ingreamount,ingreunit)
            cursor.execute(
                "UPDATE ingredient SET ingrename = %s , unit = %s, amount = %s WHERE dessertid = %s and ingredientid=%s ",
                (ingrename, ingreunit, ingreamount, id , ingreid))
            conn.commit()
            i=i+1
        conn.commit()
        conn.close()
        return redirect(url_for("profile"))
    else:
        cursor.execute(""" SELECT dessert.dessertname, qualification.cuisine, qualification.calori, qualification.serve,  qualification.timing, qualification.category,dessert.dessertrecipe, dessert.desserttype, qualification.qualificationid FROM qualification
                    INNER JOIN dessert
                    ON dessert.qualificationid = qualification.qualificationid and dessert.dessertid=%s""", (id,))
        desserts = cursor.fetchone()
        cursor.execute("SELECT ingredient.ingrename, ingredient.unit, ingredient.amount, ingredient.ingredientid FROM ingredient INNER JOIN dessert ON ingredient.dessertid = dessert.dessertid AND dessert.dessertid = %s """,(id,))
        data3 = cursor.fetchall()
        print(data3)
        cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username FROM members 
                           INNER JOIN personaldata 
                           ON personaldata.memberid = members.memberid and members.memberid = %s """,
                       (str(session["id"]),))
        memberdata = cursor.fetchall()
        conn.close()
        return render_template("change-recipe.html",  authority=session["authority"] , datam=memberdata, data=desserts , ingre=data3 , ingrelen=len(data3))


@app.route('/change-recipe/drink/<id>', methods=['GET','POST'])
def change_drink(id):
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    qualificationId = 0
    if request.method == 'POST':
        memberid = session["id"]
        qualificationid = request.form.get('qualificationid')
        name = request.form.get('recipename')
        time = request.form.get('recipetime')
        calorie = request.form.get('recipecalorie')
        country = request.form.get('recipecountry')
        type = request.form.get('recipetype')
        date = request.form.get('recipedate')
        serve = request.form.get('recipeserve')
        recipe = request.form.get('recipes')
        category = request.form.get('recipecategory')
        recipeType = request.form.get('recipeType')
        print(name , time , calorie, date , country, serve , recipe)
        cursor.execute("UPDATE qualification SET cuisine = %s , timing = %s, category = %s, calori = %s, serve= %s WHERE qualificationid = %s",
                        (country, time, category, calorie, serve, qualificationid))
        cursor.execute(
            "UPDATE beverage SET beveragename = %s , beveragerecipe = %s, beveragetype = %s WHERE beverageid = %s",
            (name, recipe, type, id))

        i=0
        while request.form.get("ingrename" + str(i)):
            ingreid = request.form.get("ingredientid"+ str(i))
            ingrename = request.form.get("ingrename" + str(i))
            ingreamount = request.form.get("ingreamount" + str(i))
            ingreunit = request.form.get("ingreunit" + str(i))
            print(ingrename,ingreamount,ingreunit)
            cursor.execute(
                "UPDATE ingredient SET ingrename = %s , unit = %s, amount = %s WHERE beverageid = %s and ingredientid=%s ",
                (ingrename, ingreunit, ingreamount, id , ingreid))
            conn.commit()
            i=i+1
        conn.commit()
        conn.close()
        return redirect(url_for("profile"))
    else:
        cursor.execute(""" SELECT beverage.beveragename, qualification.cuisine, qualification.calori, qualification.serve,  qualification.timing, qualification.category,beverage.beveragerecipe, beverage.beveragetype, qualification.qualificationid FROM qualification
                    INNER JOIN beverage
                    ON beverage.qualificationid = qualification.qualificationid and beverage.beverageid=%s""", (id,))
        drinks= cursor.fetchone()

        cursor.execute("SELECT ingredient.ingrename, ingredient.unit, ingredient.amount, ingredient.ingredientid FROM ingredient INNER JOIN beverage ON ingredient.beverageid = beverage.beverageid AND beverage.beverageid = %s """,(id,))
        data3 = cursor.fetchall()
        print(data3)
        cursor.execute("""SELECT members.memberid, personaldata.name, personaldata.surname, personaldata.location, members.e_mail, members.username FROM members 
                           INNER JOIN personaldata 
                           ON personaldata.memberid = members.memberid and members.memberid = %s """,
                       (str(session["id"]),))
        memberdata = cursor.fetchall()
        conn.close()
        return render_template("change-recipe.html",  authority=session["authority"] , datam=memberdata, data=drinks , ingre=data3 , ingrelen=len(data3))


@app.route('/file-upload', methods=['POST'])
def upload_file():
    print(request.files)
    content_length = request.content_length
    print("Content_length : {content_length}")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return jsonify ({ " text" : " No File"})

        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return jsonify ({ " text" : " File hasn't selected"})
        print(allowed_file(file.filename))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify ({ " text" : " File Uploaded Successfully"})
        return ""


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    conn = dpapi.connect(url)
    cursor = conn.cursor()
    if request.method == 'POST':

        username = ""
        if 'username' in session:
            username = session['username']

        message = request.form.get("message")
        title = request.form.get("title")
        category = request.form.get("category")
        mail = request.form.get("e_mail")
        date = request.form.get("date")
        print(message, title, category, mail)
        if message and title and category and mail:
            cursor.execute(
                "INSERT INTO contact(message, title, category, e_mail, date) VALUES (%s, %s, %s, %s, %s)",
                (message, title, category, mail, date))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))

        else:
            conn.close()
            return render_template("contact.html", username=username)
    else:
        username = ""
        if 'username' in session:
            username = session['username']
        conn.close()
        return render_template("contact.html", username=username)


if __name__ == '_main_':
    app.run(port=5000, debug=True)