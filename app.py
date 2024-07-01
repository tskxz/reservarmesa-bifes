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
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def user_loader(username):
    user_data = mongo.db.users.find_one({"username": username})
    if user_data:
        return User(username=user_data['username'], role=user_data['role'])
    return None

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        telemovel = request.form['telemovel']
        password = request.form['password']
        # Definir a role padrão como 'user'
        role = 'user'
        if mongo.db.users.find_one({"username": username}):
            flash('Nome de utilizador já existe.')
            return redirect(url_for('register_page'))

        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({"username": username, "telemovel":telemovel, "password": hashed_password, "role": role})
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
            user = User(username=user_data['username'], role=user_data['role'])
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('dashboard_page'))
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
    return render_template('protected.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))
    return render_template('dashboard.html')

@app.route('/reservar', methods=['GET', 'POST'])
@login_required
def reservar_page():
    if request.method == 'POST':
        mesa_id = request.form['mesa_id']
        data_hora = request.form['data_hora']
        pratos = request.form.getlist('prato_id')  # Lista de IDs dos pratos selecionados

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
            "aceitado": False,
            "pratos": [ObjectId(prato) for prato in pratos]  # Converter IDs para ObjectId
        }
        mongo.db.reservas.insert_one(reserva)

        # Atualizar status da mesa para reservado
        mongo.db.mesas.update_one(
            {"_id": ObjectId(mesa_id)},
            {"$set": {"reservado": True}}
        )

        flash('Reserva feita com sucesso. Aguarde a confirmação.')
        return redirect(url_for('protected_page'))

    mesas = mongo.db.mesas.find({"reservado": False})
    menus = mongo.db.menus.find()
    pratos = mongo.db.pratos.find()

    return render_template('reservar.html', mesas=mesas, menus=menus, pratos=pratos)


@app.route('/funcionarios')
@login_required
def funcionarios_page():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    funcionarios = mongo.db.funcionarios.find()
    return render_template('funcionarios.html', funcionarios=funcionarios)

@app.route('/adicionar_funcionario', methods=['POST'])
@login_required
def adicionar_funcionario():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    nome = request.form['nome']
    telemovel = request.form['telemovel']
    mongo.db.funcionarios.insert_one({"nome": nome, "telemovel": telemovel})
    flash('Funcionário adicionado com sucesso.')
    return redirect(url_for('funcionarios_page'))

@app.route('/editar_funcionario/<funcionario_id>', methods=['GET', 'POST'])
@login_required
def editar_funcionario(funcionario_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    funcionario = mongo.db.funcionarios.find_one({"_id": ObjectId(funcionario_id)})

    if request.method == 'POST':
        nome = request.form['nome']
        telemovel = request.form['telemovel']
        mongo.db.funcionarios.update_one(
            {"_id": ObjectId(funcionario_id)},
            {"$set": {"nome": nome, "telemovel": telemovel}}
        )
        flash('Funcionário atualizado com sucesso.')
        return redirect(url_for('funcionarios_page'))

    return render_template('editar_funcionario.html', funcionario=funcionario)

@app.route('/deletar_funcionario/<funcionario_id>')
@login_required
def deletar_funcionario(funcionario_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    mongo.db.funcionarios.delete_one({"_id": ObjectId(funcionario_id)})
    flash('Funcionário deletado com sucesso.')
    return redirect(url_for('funcionarios_page'))

@app.route('/mesas', methods=['GET'])
@login_required
def exibir_mesas():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    # Obter todas as mesas e funcionários para exibir no template
    mesas = mongo.db.mesas.find()
    funcionarios = mongo.db.funcionarios.find()

    # Criar um dicionário para mapear o _id do funcionário para o nome
    funcionarios_map = {funcionario['_id']: funcionario['nome'] for funcionario in funcionarios}

    # Renderizar o template 'exibir_mesas.html' passando mesas e o dicionário de funcionários
    return render_template('exibir_mesas.html', mesas=mesas, funcionarios_map=funcionarios_map)



@app.route('/mesas/criar', methods=['GET', 'POST'])
@login_required
def criar_mesa():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    if request.method == 'POST':
        identificacao = request.form['identificacao']
        quantidade_pessoas = request.form['quantidade_pessoas']
        reservado = bool(request.form.get('reservado', False))
        funcionario_id = request.form['funcionario_id']

        # Verificar se todos os campos necessários estão definidos
        if not identificacao or not quantidade_pessoas or not funcionario_id:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return redirect(url_for('criar_mesa'))

        try:
            identificacao = int(identificacao)
            quantidade_pessoas = int(quantidade_pessoas)
        except ValueError:
            flash('Identificação e quantidade de pessoas devem ser números inteiros.')
            return redirect(url_for('criar_mesa'))

        # Inserir nova mesa no MongoDB
        mongo.db.mesas.insert_one({
            "identificacao": identificacao,
            "quantidade_pessoas": quantidade_pessoas,
            "reservado": reservado,
            "funcionario_id": ObjectId(funcionario_id)
        })
        flash('Mesa adicionada com sucesso.')
        return redirect(url_for('exibir_mesas'))

    # Se não for um método POST, simplesmente renderize o template 'criar_mesa.html'
    funcionarios = mongo.db.funcionarios.find()
    return render_template('criar_mesa.html', funcionarios=funcionarios)


@app.route('/editar_mesa/<mesa_id>', methods=['GET', 'POST'])
@login_required
def editar_mesa(mesa_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    mesa = mongo.db.mesas.find_one({"_id": ObjectId(mesa_id)})

    if request.method == 'POST':
        identificacao = request.form['identificacao']
        quantidade_pessoas = request.form['quantidade_pessoas']
        reservado = bool(request.form.get('reservado', False))
        funcionario_id = request.form['funcionario_id']
        mongo.db.mesas.update_one(
            {"_id": ObjectId(mesa_id)},
            {"$set": {
                "identificacao": int(identificacao),
                "quantidade_pessoas": int(quantidade_pessoas),
                "reservado": reservado,
                "funcionario_id": ObjectId(funcionario_id)
            }}
        )
        flash('Mesa atualizada com sucesso.')
        return redirect(url_for('exibir_mesas'))


    funcionarios = mongo.db.funcionarios.find()
    return render_template('editar_mesa.html', mesa=mesa, funcionarios=funcionarios)

@app.route('/deletar_mesa/<mesa_id>')
@login_required
def deletar_mesa(mesa_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    mongo.db.mesas.delete_one({"_id": ObjectId(mesa_id)})
    flash('Mesa deletada com sucesso.')
    return redirect(url_for('exibir_mesas'))

@app.route('/menus')
@login_required
def listar_menus():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    menus = mongo.db.menus.find()
    return render_template('listar_menus.html', menus=menus)

@app.route('/menus/criar', methods=['GET', 'POST'])
@login_required
def criar_menu():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']

        if not nome:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return redirect(url_for('criar_menu'))


        mongo.db.menus.insert_one({
            "nome": nome,
            "descricao": descricao,
        })
        flash('Menu adicionado com sucesso.')
        return redirect(url_for('listar_menus'))

    return render_template('criar_menu.html')

@app.route('/menus/editar/<menu_id>', methods=['GET', 'POST'])
@login_required
def editar_menu(menu_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    menu = mongo.db.menus.find_one({"_id": ObjectId(menu_id)})

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']

        mongo.db.menus.update_one(
            {"_id": ObjectId(menu_id)},
            {"$set": {
                "nome": nome,
                "descricao": descricao,
            }}
        )
        flash('Menu atualizado com sucesso.')
        return redirect(url_for('listar_menus'))

    return render_template('editar_menu.html', menu=menu)

@app.route('/menus/deletar/<menu_id>')
@login_required
def deletar_menu(menu_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    mongo.db.menus.delete_one({"_id": ObjectId(menu_id)})
    flash('Menu deletado com sucesso.')
    return redirect(url_for('listar_menus'))

@app.route('/menus/<menu_id>/pratos', methods=['GET'])
@login_required
def listar_pratos(menu_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    menu = mongo.db.menus.find_one({"_id": ObjectId(menu_id)})
    if not menu:
        flash('Menu não encontrado.')
        return redirect(url_for('listar_menus'))

    pratos = mongo.db.pratos.find({"menu_id": ObjectId(menu_id)})
    return render_template('listar_pratos.html', menu=menu, pratos=pratos)

@app.route('/menus/<menu_id>/pratos/criar', methods=['GET', 'POST'])
@login_required
def criar_prato(menu_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])  # Converter para float (ou decimal, dependendo da precisão necessária)

        if not nome or not descricao or not preco:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return redirect(url_for('criar_prato', menu_id=menu_id))

        prato = {
            "menu_id": ObjectId(menu_id),
            "nome": nome,
            "descricao": descricao,
            "preco": preco  # Adicionando o campo preço
        }
        mongo.db.pratos.insert_one(prato)
        flash('Prato adicionado com sucesso.')
        return redirect(url_for('listar_pratos', menu_id=menu_id))

    return render_template('criar_prato.html', menu_id=menu_id)

@app.route('/pratos/<prato_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_prato(prato_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    prato = mongo.db.pratos.find_one({"_id": ObjectId(prato_id)})
    if not prato:
        flash('Prato não encontrado.')
        return redirect(url_for('listar_menus'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])  # Converter para float (ou decimal, dependendo da precisão necessária)

        if not nome or not descricao or not preco:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return redirect(url_for('editar_prato', prato_id=prato_id))

        mongo.db.pratos.update_one(
            {"_id": ObjectId(prato_id)},
            {"$set": {"nome": nome, "descricao": descricao, "preco": preco}}
        )
        flash('Prato atualizado com sucesso.')
        return redirect(url_for('listar_pratos', menu_id=prato['menu_id']))

    return render_template('editar_prato.html', prato=prato)

@app.route('/pratos/<prato_id>/deletar')
@login_required
def deletar_prato(prato_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    prato = mongo.db.pratos.find_one({"_id": ObjectId(prato_id)})
    if not prato:
        flash('Prato não encontrado.')
        return redirect(url_for('listar_menus'))

    mongo.db.pratos.delete_one({"_id": ObjectId(prato_id)})
    flash('Prato deletado com sucesso.')
    return redirect(url_for('listar_pratos', menu_id=prato['menu_id']))

@app.route('/reservas', methods=['GET'])
@login_required
def exibir_reservas():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    # Obter todas as mesas e funcionários para exibir no template
    reservas = mongo.db.reservas.find()
    users = mongo.db.users.find()
    mesas = mongo.db.mesas.find()
    users_map = {user['_id']: {'username': user['username'], 'telemovel': user['telemovel']} for user in users}
    mesas_map = {mesa['_id']: {'identificacao': mesa['identificacao'], 'quantidade_pessoas': mesa['quantidade_pessoas']} for mesa in mesas}
    # funcionarios = mongo.db.funcionarios.find()

    # Criar um dicionário para mapear o _id do funcionário para o nome
    #funcionarios_map = {funcionario['_id']: funcionario['nome'] for funcionario in funcionarios}

    # Renderizar o template 'exibir_mesas.html' passando mesas e o dicionário de funcionários
    return render_template('exibir_reservas.html', reservas=reservas, users_map=users_map, mesas_map=mesas_map)

@app.route('/deletar_reserva/<reserva_id>')
@login_required
def deletar_reserva(reserva_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    reserva = mongo.db.reservas.find_one({"_id": ObjectId(reserva_id)})
    if not reserva:
        flash('Reserva não encontrada.')
        return redirect(url_for('exibir_reservas'))

    mongo.db.reservas.delete_one({"_id": ObjectId(reserva_id)})
    
    mongo.db.mesas.update_one(
        {"_id": reserva["mesa_id"]},
        {"$set": {"reservado": False}}
    )
    flash('Reserva deletada com sucesso.')
    return redirect(url_for('exibir_reservas'))

@app.route('/aceitar_reserva/<reserva_id>')
@login_required
def aceitar_reserva(reserva_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.')
        return redirect(url_for('protected_page'))

    reserva = mongo.db.reservas.find_one({"_id": ObjectId(reserva_id)})
    if not reserva:
        flash('Reserva não encontrada.')
        return redirect(url_for('exibir_reservas'))

    mongo.db.reservas.update_one(
        {"_id": ObjectId(reserva_id)},
        {"$set": {"aceitado": True}}
    )

    mongo.db.mesas.update_one(
        {"_id": reserva["mesa_id"]},
        {"$set": {"reservado": True}}
    )

    flash('Reserva aceita com sucesso.')
    return redirect(url_for('exibir_reservas'))

# /ping - Verificar se está a funcionar
@app.route("/ping")
def ping():
    return "Pong!"

@app.route("/")
@login_required
def home():
    user = mongo.db.users.find_one({"username": current_user.id})
    user_id = user['_id']
    mesas = mongo.db.mesas.find()
    mesas_map = {mesa['_id']: {'identificacao': mesa['identificacao'], 'quantidade_pessoas': mesa['quantidade_pessoas']} for mesa in mesas}
    reservas_pendentes = mongo.db.reservas.find({"user_id": user_id, "aceitado": False})
    reservas_aceites = mongo.db.reservas.find({"user_id": user_id, "aceitado": True})

    return render_template('home.html', reservas_pendentes=reservas_pendentes, reservas_aceites=reservas_aceites, user=user, mesas_map=mesas_map)


if __name__ == '__main__':
    app.run(debug=True)
