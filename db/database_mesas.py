import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")


def setupDB(db_name):

    db = client[db_name]

    if db_name not in client.list_database_names():
        print(f"Base de dados '{db_name}' criada com sucesso!")
    
    mesas = db["mesas"]
    if "mesas" not in db.list_collection_names():
        print(f"Coleção mesas criada com sucesso!")
    return db, mesas

def inserirMesa(identificacao, quantidade_pessoas, reservado):
    base_de_dados, colecao_mesas = setupDB("reservetablebifes")
    mesa = {
        "identificacao": identificacao,
        "quantidade_pessoas": quantidade_pessoas,
        "reservado": reservado
    }
    documento_inserido = colecao_mesas.insert_one(mesa)
    if documento_inserido:
        print(f"Mesa '{identificacao}' inserido com sucesso!")

def pesquisarTodasmesas():
    base_de_dados, colecao_mesas = setupDB("reservetablebifes")
    return list(colecao_mesas.find())

def pesquisarMesaPorID(mesa_id):
    base_de_dados, colecao_mesas = setupDB("reservetablebifes")
    return colecao_mesas.find_one({"_id": mesa_id})

def atualizarMesa(mesa_id, identificacao, quantidade_pessoas, reservado):
    base_de_dados, colecao_mesas = setupDB("reservetablebifes")
    colecao_mesas.update_one({"_id": mesa_id}, {"$set": 
                           {
                               "identificacao": identificacao,
                               "quantidade_pessoas": quantidade_pessoas,
                               "reservado": reservado
                            }}
    )
    print(f"Mesa com ID {mesa_id} atualizado!")

def deletarMesa(mesa_id):
    base_de_dados, colecao_mesas = setupDB("reservetablebifes")
    colecao_mesas.delete_one({"_id": mesa_id})
    print(f"Mesa com ID {mesa_id} deletado!")


def limpar():
    base_de_dados, colecao_mesas = setupDB("reservetablebifes")
    colecao_mesas.drop()

if __name__ == "__main__":
    setupDB("reservetablebifes")

    inserirMesa(1, 4, 0)
    inserirMesa(2, 6, 1)
    inserirMesa(3, 2, 0)
    
    print("Todas as mesas:")
    for mesa in pesquisarTodasmesas():
        print(mesa)

    mesa_id = pesquisarTodasmesas()[0]["_id"]
    print(f"\nMesa com ID {mesa_id}:")
    print(pesquisarMesaPorID(mesa_id))