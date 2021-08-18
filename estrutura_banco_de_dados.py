from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, make_response
import jwt
import datetime
from functools import wraps

# Criar um API flask
app = Flask(__name__)

# # Criar um instância de SQLAlchemy
app.config['SECRET_KEY'] = 'senha'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)
db: SQLAlchemy

# Definir a estrutra da tabela Postagem: id_postagem, titulo, autor
class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


# Definir a estrutra da tabela Autor: id_autor, nome, email, senha, admin, postagens
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagem = db.relationship('Postagem')


def inicializar_banco():
    #executa c comando para criar o banco de dados
    db.drop_all()
    db.create_all()
    # Criar usuários adminstradores
    autor = Autor(nome='Eduardo', email='edugubertnasicmento@gmail.com', senha='senha123', admin=True)
    db.session.add(autor)
    db.session.commit()

if __name__ == "__main__":
    inicializar_banco()