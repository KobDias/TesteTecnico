from db import db
from flask_login import UserMixin

class Cliente(UserMixin, db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(120), nullable=False)

class Agendamentos(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)

class Clientes_Agendamentos(db.Model):
    __tablename__ = 'clientes_agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    idAgendamento = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=False)
    idCliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)