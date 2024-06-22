from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime

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
            flash('Nome de utilizador já existe.')
            return redirect(url_for('register_page'))

        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({"username": username, "password": hashed_password})
        flash('Utilizador registado com sucesso.')
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = mongo.db.users.find_one({"username": username})
        if user_data and check_password_hash(user_data['password'], password): 
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('protected_page'))
        flash('Nome de utilizador ou palavra-passe inválida.')
    return render_template('login.html')

@app.route('/logout')
def logout_page():
    if current_user.is_active:
        logout_user()
        flash('Sessão terminada com sucesso.')
        return redirect(url_for('login_page'))
    else:
        flash('Não está autenticado.')
        return redirect(url_for('login_page'))
    
@app.route('/protected_page')
@login_required
def protected_page():
    return 'Esta é uma página protegida.'

@app.route('/reservar', methods=['GET', 'POST'])
@login_required
def reservar_page():
    if request.method == 'POST':
        mesa_id = request.form['mesa_id']
        data_hora = request.form['data_hora']

        # Formatar a data e hora
        try:
            data_hora_formatada = datetime.strptime(data_hora, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Data e hora inválidas.')
            return redirect(url_for('reservar_page'))

        user_id = current_user.id

        # Inserir reserva na base de dados
        reserva = {
            "user_id": mongo.db.users.find_one({"username": user_id})['_id'],
            "mesa_id": ObjectId(mesa_id),
            "data_hora": data_hora_formatada,
            "aceitado": False
        }
        mongo.db.reservas.insert_one(reserva)
        flash('Reserva feita com sucesso. Aguarde a confirmação.')
        return redirect(url_for('protected_page'))

    mesas = mongo.db.mesas.find({"reservado": 0})
    return render_template('reservar.html', mesas=mesas)

# /ping - Verificar se está a funcionar
@app.route("/ping")
def ping():
    return "Pong!"

if __name__ == '__main__':
    app.run(debug=True)
