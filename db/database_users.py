import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb://localhost:27017/")


def setupDB(db_name):
    db = client[db_name]

    if db_name not in client.list_database_names():
        print(f"Base de dados '{db_name}' criada com sucesso!")
    
    users = db["users"]
    if "users" not in db.list_collection_names():
        print(f"Coleção users criada com sucesso!")
    return db, users

def pesquisarTodosusers():
    base_de_dados, colecao_users = setupDB("reservetablebifes")
    return list(colecao_users.find())

def pesquisarUserPorID(user_id):
    base_de_dados, colecao_users = setupDB("reservetablebifes")
    return colecao_users.find_one({"_id": ObjectId(user_id)})

def atualizarUtilizador(user_id, username):
    base_de_dados, colecao_users = setupDB("reservetablebifes")
    colecao_users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": username}})
    print(f"Utilizador com ID {user_id} atualizado!")

def atualizarPapelUtilizador(user_id, role):
    base_de_dados, colecao_users = setupDB("reservetablebifes")
    colecao_users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    print(f"Utilizador com ID {user_id} teve o papel atualizado para {role}!")

def deletarUtilizador(user_id):
    base_de_dados, colecao_users = setupDB("reservetablebifes")
    colecao_users.delete_one({"_id": ObjectId(user_id)})
    print(f"Utilizador com ID {user_id} deletado!")

def limpar():
    base_de_dados, colecao_users = setupDB("reservetablebifes")
    colecao_users.drop()

if __name__ == "__main__":
    setupDB("reservetablebifes")

    print("Todos os users:")
    for user in pesquisarTodosusers():
        print(user)

    user_id = "6677e63673edf967b0d008a0"
    print(f"\nUtilizador com ID {user_id}:")
    print(pesquisarUserPorID(user_id))

    # Atualizar papel do utilizador para 'admin'
    atualizarPapelUtilizador(user_id, "admin")

    print(f"\nUtilizador com ID {user_id} após atualização de papel:")
    print(pesquisarUserPorID(user_id))
