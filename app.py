from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "sh!"
app.config["MONGO_URI"] = "mongodb://localhost:27017/reservetablebifes"
mongo = PyMongo(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Define a view de login padrão

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user_data = mongo.db.users.find_one({"username": username})
    if user_data:
        user = User()
        user.id = username
        return user
    return None

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if mongo.db.users.find_one({"username": username}):
            flash('Username already exists.')
            return redirect(url_for('register_page'))

        mongo.db.users.insert_one({"username": username, "password": password})
        flash('User registered successfully.')
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # autenticar as credenciais
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('protected_page'))
    return render_template('login.html')

@app.route('/logout')
def logout_page():
    if current_user.is_active:
        logout_user()
        return 'Logged out'
    else:
        return "you aren't login"
    
@app.route('/protected_page')
@login_required
def protected_page():
    return 'This is a protected page.'


# /ping - Verificar se está a funcionar
@app.route("/ping")
def ping():
    return "Pong!"