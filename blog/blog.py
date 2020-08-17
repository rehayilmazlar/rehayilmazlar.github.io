from functools import wraps
from flask import Flask, render_template, request, session, url_for, redirect, flash, jsonify
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256
import os
from stocks import usdTotry, eurTotry, goldTotry
import datetime
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import json
class FoodForm(Form):
    name = StringField("Enter a food name" , validators=[validators.Length(min=1,max=40)])
    foodArea = TextAreaField("Input recipe here")



app = Flask(__name__)

app.config["MYSQL_HOST"] = "192.168.181.134"
app.config["MYSQL_USER"] = "reha"
app.config["MYSQL_PASSWORD"] = "19901991"
app.config["MYSQL_DB"] ="rehasblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


#Kullanıcı giriş decorator'ı

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggedin" in session:
            return f(*args, **kwargs)
        else:
            return render_template("error.html")
    return decorated_function

def admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usergroup = sql_select('usergroup','users','name',session['username'])
        usergroup = usergroup[0]['usergroup']
        if usergroup == 'admin':
            return f(*args, **kwargs)
        else:
            cursor = mysql.connection.cursor()
            sorgu = "SELECT * FROM users"
            cursor.execute(sorgu)
            data = cursor.fetchall()
            for i in data:
                i["time"] = i["time"].strftime("%d-%b-%Y %H:%M:%S")
            cursor.close()
            return render_template('users.html', data=data)
    return decorated_function
def sql_select_all(tbl):
    with app.app_context():#flask bunsuz sql sorgusu yapmıyor!
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM " + tbl
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result


def sql_select(columns, tbl, where_param, val):
    columns2 = ""
    if type(columns) == type([1,2]):
        for i in range (0, len(columns)):
            if i == len(columns)-1:
                columns2 += columns[i]
                break
            columns2 += columns[i] + ', '
    else:
        columns2 = columns
    columns2 = str(("SELECT %s FROM %s WHERE %s = ")%(columns2, tbl, where_param ))
    query = columns2 + "%s"
    with app.app_context():#flask bunsuz sql sorgusu yapmıyor!
        cursor = mysql.connection.cursor()
        cursor.execute(query, (val, ))
        result = cursor.fetchall()
        cursor.close()
        return result

def sql_update(tbl, columns, col_values, where_param, val):
    columns2 = ""
    if type(columns) == type([1,2]):
        for i in range (0, len(columns)):
            if i == len(columns)-1:
                columns2 += columns[i] + "='%s'"
                break
            columns2 += columns[i] + "= '%s', "
    else:
        columns2 = columns + "= '%s'"

    col_values2 = ""
    if type(col_values) == type([1,2]):
        for i in range (0, len(col_values)):
            if i == len(col_values)-1:
                col_values2 += str(col_values[i])
                break
            col_values2 += str(col_values[i]) + ','
    else:
        col_values2 = str(col_values)
        
    final_col = col_values2.split(',')

    for col in final_col:
        columns2 = columns2.replace('%s',col,1)

    query = str(("UPDATE %s SET %s WHERE %s = ")%(tbl, columns2, where_param))
    query2 = query + '%s'
    with app.app_context():#flask bunsuz sql sorgusu yapmıyor!
        cursor = mysql.connection.cursor()
        cursor.execute(query2, (val, ))
        mysql.connection.commit()
        cursor.close()

def sql_update_dic(tbl, column, dic, where_param, val):

    query = "UPDATE " + tbl + " SET " + column + " = \"" +dic + "\" WHERE " + where_param + " = " + str(val)
    with app.app_context():#flask bunsuz sql sorgusu yapmıyor!
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()

def sql_insert(tbl, columns, col_values):
    columns2 = ""
    if type(columns) == type([1,2]):
        for i in range (0, len(columns)):
            if i == len(columns)-1:
                columns2 += columns[i]
                break
            columns2 += columns[i] + ', '
    else:
        columns2 = columns
        
    col_values2=""
    if type(col_values) == type([1,2]):
        for i in range (0, len(col_values)):
            if i == len(col_values)-1:
                col_values2 += "'" + str(col_values[i]) + "'"
                break
            col_values2 += "'" + str(col_values[i]) + "'" + ', '
    else:
        col_values2 = "'"+ str(col_values) + "'"
    query = str(("INSERT INTO %s (%s) VALUES (%s) ")%(tbl, columns2, col_values2))

    with app.app_context():#flask bunsuz sql sorgusu yapmıyor!
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()


def sql_delete(tbl, where_param, val):
    query = "DELETE FROM " + tbl +" WHERE " + where_param + " = " + "%s"
    with app.app_context():#flask bunsuz sql sorgusu yapmıyor sayfadan bağımsız!
        cursor = mysql.connection.cursor()
        cursor.execute(query, (val, ))
        mysql.connection.commit()
        cursor.close()

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        passw = request.form['passw']
        passw2 = request.form['passw2']
        now = datetime.datetime.now()
        
        usergroup = 'user'
        cursor = mysql.connection.cursor()
        if username == '':
            flash("Enter a username!", category="danger")
            return redirect(url_for("register"))
        elif passw == '':
            flash("Enter a password", category="danger")
            return redirect(url_for("register"))
        elif passw != passw2:
            flash("Passwords do not match!", category="danger")
            return redirect(url_for("register"))
        else:
            data = sql_select('name','users', 'name', username)
            if data:
                flash("User exists!", category="danger")
                return redirect(url_for("register"))
            else:
                passw = pbkdf2_sha256.hash(passw)
                sql_insert('users', ['name', 'password', 'usergroup', 'time'], [username, passw, usergroup, now])
                cursor = mysql.connection.cursor()
                cursor.callproc('CorrectId') #stored procedure id'leri güncellemek için
                cursor.close()
                session["loggedin"] = True
                session["username"] = username
                flash("Successfully registered!", category="success")
                return redirect(url_for("index"))
    else:    
        return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        passw = request.form['passw']
        try:
            data = sql_select('password', 'users', 'name', username)
            if pbkdf2_sha256.verify(passw, data[0]["password"]):
                session["loggedin"] = True

                session["username"] = username
                flash("Login successful!", category='info')
                return redirect(url_for("index"))
            else:
                flash("Wrong name or password!",category="warning")
                return redirect(url_for("login")) 
        except Exception as e:
            flash("User doesn't exist!" + str(e),category="dark")
            return redirect(url_for("login")) 
    else:
        return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/admin")
@login_required
@admin
def users():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM users"
    cursor.execute(sorgu)
    data = cursor.fetchall()
    for i in data:
        i["time"] = i["time"].strftime("%d-%b-%Y %H:%M:%S")
    cursor.close()
    return render_template("admin.html", data=data)

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    sql_delete('users', 'id', id)
    cursor = mysql.connection.cursor()
    cursor.callproc('CorrectId')
    cursor.close()
    return redirect(url_for("users"))

@app.route("/update/<string:id>", methods = ["GET", "POST"])
@login_required
def update(id):
    data = sql_select(['name','password'], 'users', 'id', id)
    username = data[0]["name"]
    if request.method == "POST":
        user = request.form['username']
        password = request.form['passw']
        password = pbkdf2_sha256.hash(password)
        group2 = request.form.values()
        group2 = list(group2)
        group2.pop(0)
        if 'admin' in group2:
            usergroup= 'admin'
        elif "Choose user group!" in group2:
            flash("Please select a user group!", category="warning")
            return render_template("update.html", username=username,passw='password', id=id)
        else:
            usergroup = 'user'
        sql_update('users',['name', 'password', 'usergroup'],[user,password,usergroup], 'id', id)
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM users"
        cursor.execute(sorgu)
        data = cursor.fetchall()
        cursor.close()
        flash("User info has been succesfully updated!", category="primary")
        return redirect(url_for('users'))
    else:
        return render_template("update.html", username=username,passw='password', id=id)
@app.route("/stocks", methods = ["GET", "POST"])
@login_required
def stocks():
    usd = float(usdTotry().replace(',','.'))
    eur = float(eurTotry().replace(',','.'))
    gold =float(goldTotry().replace(',','.'))
    day = datetime.datetime.now().strftime("%d %B %Y")
    username = session['username']
    data = sql_select('id', 'users', 'name', username)
    userid = data[0]['id']
    data2 = sql_select('*', 'stocks','userid', userid)
    if (data2 and request.method == "GET"):
        eur_quantity = data2[0]['eur']
        usd_quantity = data2[0]['usd']
        gold_quantity = data2[0]['gold']
        eur_amount = format(eur_quantity * eur, ',.3f')
        usd_amount = format(usd_quantity * usd, ',.3f')
        gold_amount = format(gold_quantity * gold, ',.3f')
        total = format((eur_quantity * eur) +(usd_quantity * usd) + (gold_quantity * gold), ',.3f')
        return render_template("stocks.html", total=total, userid=userid, eur_quantity=eur_quantity,gold_quantity=gold_quantity,usd_quantity=usd_quantity, eur=eur, usd=usd, date=day, gold=gold, eur_amount=eur_amount, usd_amount=usd_amount, gold_amount=gold_amount)

    elif request.method == "POST":
        usd_form = request.form['usd_form'].replace(',','.')
        eur_form = request.form['eur_form'].replace(',','.')
        gold_form = request.form['gold_form'].replace(',','.')
        try:
            usd_form =float(usd_form)
            eur_form =float(eur_form)
            gold_form =float(gold_form)
            if data2:
                    eur_quantity = data2[0]['eur']
                    usd_quantity = data2[0]['usd']
                    gold_quantity = data2[0]['gold']
                    eur_amount = format(eur_quantity * eur, ',.3f')
                    usd_amount = format(usd_quantity * usd, ',.3f')
                    gold_amount = format(gold_quantity * gold, ',.3f')
                    
                    sql_update('stocks', ['userid', 'usd', 'eur', 'gold'], [userid, usd_form, eur_form, gold_form], 'userid', userid)
                    return redirect(url_for('stocks'))
                
        except Exception:
            visible=True
            eur_quantity = data2[0]['eur']
            usd_quantity = data2[0]['usd']
            gold_quantity = data2[0]['gold']
            eur_amount = format(eur_quantity * eur, ',.3f')
            usd_amount = format(usd_quantity * usd, ',.3f')
            gold_amount = format(gold_quantity * gold, ',.3f')
            flash("Enter numbers!", category='danger')
            return render_template("stocks.html", visible=visible,eur_quantity=eur_quantity,gold_quantity=gold_quantity,usd_quantity=usd_quantity, eur=eur, usd=usd, date=day, gold=gold, eur_amount=eur_amount, usd_amount=usd_amount, gold_amount=gold_amount )
        
           
    else:
        sql_insert('stocks',['userid', 'usd', 'eur', 'gold'], [userid,0,0,0])
        data3 = sql_select('*', 'stocks', 'userid', userid )
        eur_quantity = data3[0]['eur']
        usd_quantity = data3[0]['usd']
        gold_quantity = data3[0]['gold']
        eur_amount = format(eur_quantity * eur, ',.3f')
        usd_amount = format(usd_quantity * usd, ',.3f')
        gold_amount = format(gold_quantity * gold, ',.3f')
        total = format((eur_quantity * eur) +(usd_quantity * usd) + (gold_quantity * gold), ',.3f')
        return render_template("stocks.html", total=total, userid=userid, eur_quantity=eur_quantity,gold_quantity=gold_quantity,usd_quantity=usd_quantity, eur=eur, usd=usd, date=day, gold=gold, eur_amount=eur_amount, usd_amount=usd_amount, gold_amount=gold_amount)
    

@app.route("/food_list")
@login_required
def food_list():
    cursor = mysql.connection.cursor()
    cursor.callproc('CorrectFoodId')
    sorgu = "SELECT * FROM food"
    cursor.execute(sorgu)
    food = cursor.fetchall()
    if food:
        food_id = food[-1]['id']
    else:
        food_id = 0
    for i in food:
        i["time"] = i["time"].strftime("%d-%b-%Y %H:%M:%S")
    cursor.close()
    return render_template("food_list.html", food=food, id=food_id+1, )  
@app.route("/food/<string:id>")
def food(id):
    food = sql_select('*','food','food.id',id)
    food2 =food
    food = food[0]
    print(food)
    ing = food2[0]['ingredients'].replace("'","\"")
    ing = json.loads(ing)
    ing = list(ing.values())    
    ingredients = [ ing [i:i + 3] for i in range(0, len(ing), 3) ]
    for i in range (0, len(ingredients)):
        ingredients[i].insert(0,i+1)
        continue
    
    content = food['content']
    print(content)
    return render_template("food.html", food=food, ingredients=ingredients, content=content) 

@app.route("/delete_stocks/<string:id>")
@login_required
def delete_stocks(id):
    sql_delete('stocks', 'userid', id)
    return redirect(url_for("stocks"))


@app.route("/add_food_2/<string:id>", methods = ['GET', 'POST'])
@login_required
def add_food_2(id):
    ingredients = sql_select_all('ing')
    quantities = sql_select_all('qty')
    measures = sql_select_all('msr')
    
    name = sql_select('name','food','food.id',id)
    if request.method =="POST":
        dic = dict(request.form.items())
        print(dic)
        ingredients_dic = dic.copy()
        ingredients_dic.pop('qty_form')
        ingredients_dic.pop('ing_form')
        ingredients_dic.pop('msr_form')
        ingredients_dic = str(ingredients_dic)
        sql_update_dic('food','ingredients',ingredients_dic,'id',id)
        if 'ing_form' in dic and dic['ing_form'] !='':
            print("ING_FORM!!!!!!!!!!!")
            if sql_select('ingredient','ing', 'ingredient',dic['ing_form']):
                flash("You already have this ingredient!", category="warning")
            else:
                print("2 ING_FORM!!!!!!!!!!!")
                sql_insert('ing','ingredient',dic['ing_form'])
        if 'qty_form' in dic and dic['qty_form'] !='':
            if sql_select('quantity','qty','quantity', dic['qty_form']):
                flash("You already have this quantity!", category="warning")
            else:
                sql_insert('qty','quantity',dic['qty_form'])
        if 'msr_form' in dic and dic['msr_form'] !='':
            if sql_select('measure','msr','measure', dic['msr_form']):
                flash("You already have this measure!", category="warning")
            else:
                sql_insert('msr','measure',dic['msr_form'])
            return redirect(url_for('add_food_2', id=id)) 
        else:
            name = sql_select('name','food','food.id',id)
            name = name[0]["name"]
            return redirect(url_for('add_food_3', id=id))

    else:
        name = name[0]["name"]
        return render_template("/add_food_2.html", name=name, msr=measures, qty=quantities, ing=ingredients) 


@app.route("/delete_food/<string:id>")
def delete_food(id):
    cursor = mysql.connection.cursor()
    sql_delete('food','id',id)
    cursor.callproc('CorrectFoodId')
    cursor.close()
    flash("Food has been deleted!", "warning")
    return redirect(url_for('food_list'))

    
@app.route("/add_food_1/<string:id>", methods=['POST','GET'])
@login_required
def add_food_1(id):
    if request.method =="POST":
        name = request.form["food_name"].strip()
        if sql_select('name','food','name',name):
            flash("You already have this food!", category="danger")
            return redirect(url_for('add_food_1', id=id))
        else:
            now = datetime.datetime.now()
            username = session['username']
            cursor = mysql.connection.cursor()
            sql_insert('food',['name', 'time', 'author'],[name, now, username])
            cursor.callproc('CorrectFoodId')
            cursor.close()
            return redirect(url_for('add_food_2', id=id))
    else:
        return render_template("add_food_1.html")


@app.route("/add_food_3/<string:id>", methods=['POST','GET'])
@login_required
def add_food_3(id):
    if request.method =="POST":
        content = request.form["content"].replace("\"", "'")
        print(content)
        sql_update_dic('food','content', content,'id', id)
        name = sql_select('name','food','food.id',id)
        name = name[0]["name"]
        return redirect(url_for('food', id=id))
    else:
        name = sql_select('name','food','food.id',id)
        name = name[0]["name"]
        return render_template("add_food_3.html" , name=name)





@app.route("/test")
def test():
    return render_template("test.html")
if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=80, debug=True)

