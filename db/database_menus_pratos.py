import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

def setupDB(db_name):
    db = client[db_name]

    if db_name not in client.list_database_names():
        print(f"Base de dados '{db_name}' criada com sucesso!")

    menus = db["menus"]
    pratos = db["pratos"]

    if "menus" not in db.list_collection_names():
        print(f"Colecao 'menus' criada com sucesso!")

    if "pratos" not in db.list_collection_names():
        print(f"Colecao 'pratos' criada com sucesso!")

    return db, menus, pratos

def inserirMenu(nome, descricao):
    base_de_dados, colecao_menus, _ = setupDB("reservetablebifes")
    
    if colecao_menus.find_one({"nome": nome}):
        print(f"Menu com o nome '{nome}' já existe.")
        return

    menu = {
        "nome": nome,
        "descricao": descricao
    }
    documento_inserido = colecao_menus.insert_one(menu)
    if documento_inserido:
        print(f"Menu '{nome}' inserido com sucesso!")

def listarMenus():
    base_de_dados, colecao_menus, _ = setupDB("reservetablebifes")
    menus = colecao_menus.find()
    for menu in menus:
        print(f"Nome: {menu['nome']}, Descrição: {menu['descricao']}")

def deletarMenu(nome):
    base_de_dados, colecao_menus, _ = setupDB("reservetablebifes")
    resultado = colecao_menus.delete_one({"nome": nome})
    if resultado.deleted_count > 0:
        print(f"Menu '{nome}' deletado com sucesso!")
    else:
        print(f"Menu '{nome}' não encontrado.")

def inserirPrato(menu_nome, nome_prato, descricao, preco):
    base_de_dados, colecao_menus, colecao_pratos = setupDB("reservetablebifes")

    menu = colecao_menus.find_one({"nome": menu_nome})
    if not menu:
        print(f"Menu '{menu_nome}' não encontrado.")
        return

    prato = {
        "menu_id": menu["_id"],
        "nome": nome_prato,
        "descricao": descricao,
        "preco": preco
    }
    documento_inserido = colecao_pratos.insert_one(prato)
    if documento_inserido:
        print(f"Prato '{nome_prato}' inserido com sucesso no menu '{menu_nome}'.")

def listarPratos(menu_nome):
    base_de_dados, colecao_menus, colecao_pratos = setupDB("reservetablebifes")

    menu = colecao_menus.find_one({"nome": menu_nome})
    if not menu:
        print(f"Menu '{menu_nome}' não encontrado.")
        return

    pratos = colecao_pratos.find({"menu_id": menu["_id"]})
    print(f"Pratos no menu '{menu_nome}':")
    for prato in pratos:
        print(f"Nome: {prato['nome']}, Descrição: {prato['descricao']}, Preço: {prato['preco']}")

# Exemplo de uso
if __name__ == "__main__":
    # Inserir um novo menu
    inserirMenu("Menu Delícias", "Um menu cheio de delícias.")
    inserirMenu("Menu Carnes", "Menu especial para os amantes de carnes.")

    # Listar todos os menus
    print("Menus cadastrados:")
    listarMenus()

    # Inserir pratos nos menus
    inserirPrato("Menu Delícias", "Prato 1", "Descrição do Prato 1", 29.99)
    inserirPrato("Menu Carnes", "Prato 2", "Descrição do Prato 2", 49.99)

    # Listar pratos de um menu específico
    listarPratos("Menu Delícias")
    listarPratos("Menu Carnes")

    # Deletar um menu
    deletarMenu("Menu Delícias")

    # Listar todos os menus após a exclusão
    print("Menus cadastrados após exclusão:")
    listarMenus()
