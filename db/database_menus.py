import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")

def setupDB(db_name):
    db = client[db_name]

    if db_name not in client.list_database_names():
        print(f"Base de dados '{db_name}' criada com sucesso!")

    menus = db["menus"]
    if "menus" not in db.list_collection_names():
        print(f"Colecao menus criada com sucesso!")
    return db, menus

def inserirMenu(nome, descricao, preco):
    base_de_dados, colecao_menus = setupDB("reservetablebifes")
    menu = {
        "nome": nome,
        "descricao": descricao,
        "preco": preco
    }
    documento_inserido = colecao_menus.insert_one(menu)
    if documento_inserido:
        print(f"Menu '{nome}' inserido com sucesso!")