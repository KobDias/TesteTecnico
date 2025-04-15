from db import db
from flask_login import UserMixin
import enum

class Cliente(UserMixin, db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Campo para identificar administradores

class Estado(enum.Enum):
        pendente = "pendente"
        finalizado = "finalizado"
        cancelado = "cancelado"

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text)

class Agendamentos(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    clienteId = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.Enum(Estado), default=Estado.pendente, nullable=False)
    cliente = db.relationship('Cliente', backref='agendamentos')
    is_confirmed = db.Column(db.Boolean, default=False)


agendamento_servico = db.Table('agendamento_servico',
    db.Column('agendamento_id', db.Integer, db.ForeignKey('agendamentos.id')),
    db.Column('servico_id', db.Integer, db.ForeignKey('servico.id'))
)

Agendamentos.servicos = db.relationship(
    'Servico',
    secondary=agendamento_servico,
    backref=db.backref('agendamentos', lazy='dynamic')
)
