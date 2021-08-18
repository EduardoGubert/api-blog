from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db
import jwt
import datetime
from functools import wraps

#Rota padrão - GET https://localhost:5000


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        # Se temos um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'])
            autor = Autor.query.filter_by(
                id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token é inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated

@app.route('/login')
def login():
    dados_autoricacao = request.authorization
    if not dados_autoricacao or not dados_autoricacao.username or not dados_autoricacao.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório!"'})

    user = Autor.query.filter_by(nome=dados_autoricacao.username).first()
    if user.senha == dados_autoricacao.password:
        token = jwt.encode({'id_autor': user.id_autor, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório!"'})

@app.route('/')
@token_obrigatorio
def obter_todas_postagens(autor):
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_de_postagens.append(postagem_atual)

    return jsonify({'postagens': lista_de_postagens})


# Obter postagem por id - GET https://localhost:5000/postagem/1

@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_id(autor,id_postagem):
    postagem = Postagem.query.filter_by(id_autor=id_postagem).first()
    postagem_atual = {}
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    postagem_atual['id_autor'] = postagem.id_autor
    return jsonify({'postagem': postagem_atual})



# Criar uma nova postagem - POST https://localhost:5000/postagem

@app.route('/postagens', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criado com sucesso'}, 200)


# Alterar uma postagem existente - PUT https://localhost:5000/postagem/1

@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def atualizar_postagem(autor,id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify({'mensagem:' 'Postagem não encontrado'})
    try:
        postagem.nome = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.email = postagem_alterada['id_autor']
    except:
        pass


    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterado com sucesso!'}, 200)


# Excluir uma postagem - DELETE - https://localhost:5000/postagem/1

@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor,id_postagem):
    postagem_a_ser_excluida = Postagem.query.filter_by(id_postagem=id_postagem)
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem' : 'Não foi encontrado uma postagem com este id'})

    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()
    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})



# Criar uma api para criar novos autores
@app.route('/autores', methods=['GET'])
@token_obrigatorio
def obter_todos_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)
    return jsonify({'autores': lista_de_autores})



@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor,id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify(f'Autor não encontrado!')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    return jsonify({'autor':autor_atual})

# Criar novo autor

@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
   novo_autor = request.get_json()
   autor = Autor(
       nome=novo_autor['nome'],senha=novo_autor['senha'], email=novo_autor['email'])

   db.session.add(autor)
   db.session.commit()

   return jsonify({'mensagem': 'Usuário criado com sucesso'}, 200)


@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def atualizar_ator(autor,id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'mensagem:' 'Autor não encontrado'})
    try:
        autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
         autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        autor.senha = usuario_a_alterar['senha']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Usuário alterado com sucesso!'}, 200)


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor,id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor_existente:
        return jsonify({'mensagem': 'Autor não encontrado '})

    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluído com sucesso!'})



app.run(port=5000, host='localhost', debug=True)