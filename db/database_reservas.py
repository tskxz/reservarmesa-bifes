import pymongo
from bson.objectid import ObjectId
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")

def setupDB(db_name):
    db = client[db_name]
    if db_name not in client.list_database_names():
        print(f"Base de dados '{db_name}' criada com sucesso!")
    
    reservas = db["reservas"]
    if "reservas" not in db.list_collection_names():
        print(f"Coleção reservas criada com sucesso!")
    return db, reservas

def inserirReserva(user_id, mesa_id, data_hora, aceitado):
    base_de_dados, colecao_reservas = setupDB("reservetablebifes")
    reserva = {
        "user_id": ObjectId(user_id),
        "mesa_id": ObjectId(mesa_id),
        "data_hora": datetime.strptime(data_hora, '%Y-%m-%dT%H:%M:%S'),
        "aceitado": aceitado
    }
    documento_inserido = colecao_reservas.insert_one(reserva)
    if documento_inserido:
        print(f"Reserva para o utilizador '{user_id}' inserida com sucesso!")

def pesquisarTodasReservas():
    base_de_dados, colecao_reservas = setupDB("reservetablebifes")
    return list(colecao_reservas.find())

def pesquisarReservaPorID(reserva_id):
    base_de_dados, colecao_reservas = setupDB("reservetablebifes")
    return colecao_reservas.find_one({"_id": ObjectId(reserva_id)})

def atualizarReserva(reserva_id, user_id, mesa_id, data_hora, aceitado):
    base_de_dados, colecao_reservas = setupDB("reservetablebifes")
    colecao_reservas.update_one({"_id": ObjectId(reserva_id)}, {"$set": 
                           {
                               "user_id": ObjectId(user_id),
                               "mesa_id": ObjectId(mesa_id),
                               "data_hora": datetime.strptime(data_hora, '%Y-%m-%dT%H:%M:%S'),
                               "aceitado": aceitado
                            }}
    )
    print(f"Reserva com ID {reserva_id} atualizada!")

def deletarReserva(reserva_id):
    base_de_dados, colecao_reservas = setupDB("reservetablebifes")
    colecao_reservas.delete_one({"_id": ObjectId(reserva_id)})
    print(f"Reserva com ID {reserva_id} deletada!")

def limpar():
    base_de_dados, colecao_reservas = setupDB("reservetablebifes")
    colecao_reservas.drop()

if __name__ == "__main__":
    setupDB("reservetablebifes")

    # Adicionar código de exemplo para inserir, atualizar, pesquisar e deletar reservas.
    # Exemplo de utilização:
    user_id = "6676a8dac82b64e76d0ab71e" 
    mesa_id = "6676ae3f52a27c21890d407d" 
    inserirReserva(user_id, mesa_id, "2024-06-22T19:00:00", False)

    print("Todas as reservas:")
    for reserva in pesquisarTodasReservas():
        print(reserva)

    reserva_id = pesquisarTodasReservas()[0]["_id"]
    print(f"\nReserva com ID {reserva_id}:")
    print(pesquisarReservaPorID(reserva_id))
    
    atualizarReserva(reserva_id, user_id, mesa_id, "2023-06-22T19:00:00", True)
    print(f"\nReserva com ID {reserva_id} após atualização:")
    print(pesquisarReservaPorID(reserva_id))
    
    deletarReserva(reserva_id)
    print(f"\nTodas as reservas após deletar a reserva com ID {reserva_id}:")
    for reserva in pesquisarTodasReservas():
        print(reserva)
