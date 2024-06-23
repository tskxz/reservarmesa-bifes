import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

def setupDB(db_name):
    db = client[db_name]

    if db_name not in client.list_database_names():
        print(f"Base de dados '{db_name}' criada com sucesso!")
    
    funcionarios = db["funcionarios"]
    if "funcionarios" not in db.list_collection_names():
        print(f"Coleção funcionarios criada com sucesso!")
    return db, funcionarios

def inserirFuncionario(nome, telemovel):
    base_de_dados, colecao_funcionarios = setupDB("reservetablebifes")
    funcionario = {
        "nome": nome,
        "telemovel": telemovel
    }
    documento_inserido = colecao_funcionarios.insert_one(funcionario)
    if documento_inserido:
        print(f"Funcionário '{nome}' inserido com sucesso!")

def pesquisarTodosFuncionarios():
    base_de_dados, colecao_funcionarios = setupDB("reservetablebifes")
    return list(colecao_funcionarios.find())

def pesquisarFuncionarioPorID(funcionario_id):
    base_de_dados, colecao_funcionarios = setupDB("reservetablebifes")
    return colecao_funcionarios.find_one({"_id": funcionario_id})

def atualizarFuncionario(funcionario_id, nome, telemovel):
    base_de_dados, colecao_funcionarios = setupDB("reservetablebifes")
    colecao_funcionarios.update_one({"_id": funcionario_id}, {"$set": 
                           {
                               "nome": nome,
                               "telemovel": telemovel
                            }}
    )
    print(f"Funcionário com ID {funcionario_id} atualizado!")

def deletarFuncionario(funcionario_id):
    base_de_dados, colecao_funcionarios = setupDB("reservetablebifes")
    colecao_funcionarios.delete_one({"_id": funcionario_id})
    print(f"Funcionário com ID {funcionario_id} deletado!")

def limpar():
    base_de_dados, colecao_funcionarios = setupDB("reservetablebifes")
    colecao_funcionarios.drop()

if __name__ == "__main__":
    setupDB("reservetablebifes")

    inserirFuncionario("João Silva", "123456789")
    inserirFuncionario("Maria Oliveira", "987654321")
    inserirFuncionario("Ana Costa", "123123123")
    
    print("Todos os funcionários:")
    for funcionario in pesquisarTodosFuncionarios():
        print(funcionario)

    funcionario_id = pesquisarTodosFuncionarios()[0]["_id"]
    print(f"\nFuncionário com ID {funcionario_id}:")
    print(pesquisarFuncionarioPorID(funcionario_id))
