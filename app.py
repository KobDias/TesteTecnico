from collections import defaultdict
from flask import Flask, flash, url_for, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from db import db
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import hashlib

app = Flask(__name__)
app.secret_key = "m04H4H4"
lm = LoginManager(app)
lm.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabeleleila.db'
db.init_app(app)

from models import Cliente, Agendamentos, Servico, Estado

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader

def load_user(id):
    cliente = db.session.query(Cliente).filter_by(id=id).first()
    return cliente

@app.route('/')
def home():
    if current_user.is_authenticated:
        # Lógica de avisos
        agendamentos = Agendamentos.query.filter_by(clienteId=current_user.id).order_by(Agendamentos.data.asc()).all()
        hoje = datetime.now()
        
        # Agrupar agendamentos por semana
        agendamentos_por_semana = defaultdict(list)
        for agendamento in agendamentos:
            ano, semana, _ = agendamento.data.isocalendar()
            agendamentos_por_semana[(ano, semana)].append(agendamento)

        # Filtrar semanas com múltiplos agendamentos
        semanas_com_multiplos = {semana: ags for semana, ags in agendamentos_por_semana.items() if len(ags) > 1}

        agendamentos = Agendamentos.query.filter_by(clienteId=current_user.id).all()  # Busca os agendamentos do usuário
        # if agendamentos.data
        for agendamento in agendamentos:
            servicos = Servico.query.join(Agendamentos.servicos).filter(Agendamentos.id == agendamento.id).all()
            agendamento.servicos = servicos
        return render_template('index.html',
            agendamentos=agendamentos,
            semanas_com_multiplos=semanas_com_multiplos,
            hoje=hoje)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cliente = db.session.query(Cliente).filter_by(email=email, senha=hash(senha)).first()
        if cliente: # se realmente cliente
            login_user(cliente)
            return redirect(url_for('home'))
        else:
            return "Email ou senha invalidos"
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']

        novo_cliente = Cliente(nome=nome, email=email, telefone=telefone, senha=hash(senha))
        db.session.add(novo_cliente)
        db.session.commit()
        login_user(novo_cliente)
        return redirect(url_for('home'))
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/agendamentos', methods=['GET', 'POST'])
@login_required
def agendamentos():
    if request.method == 'POST':
        # Obter dados do formulário
        dataHora = datetime.strptime(request.form.get('dataHora'), '%Y-%m-%dT%H:%M')
        servicos_ids = request.form.getlist('servicos')
        if dataHora < datetime.now() or servicos_ids==[]:
            return "Não é possivel marcar uma data passada ou deixar de escolher um serviço!"
        else:
        # Criar agendamento
            novo_agendamento = Agendamentos(
                clienteId=current_user.id,
                data=dataHora,       
            )
            for servico_id in servicos_ids:
                servico = Servico.query.get(servico_id)
                if servico:
                    novo_agendamento.servicos.append(servico)
        
            db.session.add(novo_agendamento)
            db.session.commit()

        return redirect(url_for('home'))
    
    # Carregar serviços disponíveis para o formulário
    servicos = Servico.query.all()
    return render_template('criarAgendamento.html', servicos=servicos)

@app.route('/editarAgendamento/<int:id>', methods=['GET', 'POST'])
@login_required
def editarAgendamento(id):
    agendamento = Agendamentos.query.get_or_404(id)
    todos_servicos = Servico.query.all()  # Todos os serviços disponíveis
    if request.method == 'POST':
        dataAgendado = agendamento.data
        dataHoje = datetime.now()
        distancia = (dataAgendado - dataHoje).days
        if abs(distancia) < 2:
            return "Infelizmente, edições só podem ser feitas até dois dias antes do agendamento. Ligue para a Leila em 55555555 para alterações."
        # Atualizar os dados do agendamento conforme necessário
        else:
            agendamento.data = datetime.strptime(request.form.get('dataHora'), '%Y-%m-%dT%H:%M')
            novo_estado = request.form.get('estado')
            novos_servicos_ids = request.form.getlist('servicos') # pega as strings selecionadas
            ids_atuais = {s.id for s in agendamento.servicos} # pega os ids atualmente selecionados
            novos_ids = set(map(int, novos_servicos_ids)) # converte para os ids
            if not novos_servicos_ids:
                flash('Selecione pelo menos um serviço!', 'error')
                return "Não é possivel deixar o agendamento sem serviços"
            para_remover = ids_atuais - novos_ids  # calcula as diferenças
            for servico_id in para_remover: # remove elas
                servico = Servico.query.get(servico_id)
                if servico:
                    agendamento.servicos.remove(servico)

            para_adicionar = novos_ids - ids_atuais # calcula os adicionais
            for servico_id in para_adicionar: # adiciona elas
                servico = Servico.query.get(servico_id)
                if servico:
                    agendamento.servicos.append(servico)
            agendamento.estado = Estado[novo_estado]  # Converte a string para o enum
            try:
                db.session.commit()
                flash('Agendamento atualizado com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao salvar: {str(e)}', 'error')
            return redirect(url_for('home'))
    servicos = Servico.query.all()
    return render_template('editarAgendamento.html', agendamento=agendamento, servicos=servicos, estados=Estado, todos_servicos=todos_servicos)

@app.route('/cancelarAgendamento/<int:id>', methods=['POST', 'GET'])
@login_required
def cancelarAgendamento(id):
    if request.method == 'POST':
        agendamento = Agendamentos.query.get_or_404(id)
        dataAgendado = agendamento.data
        dataHoje = datetime.now()
        distancia = (dataAgendado - dataHoje).days
        if abs(distancia) < 2:
            return "Infelizmente, cancelamentos só podem ser feitos até dois dias antes do agendamento. Ligue para a Leila em 55555555 para alterações."
        else:
            agendamento.estado = Estado.cancelado
            db.session.add(agendamento)
            db.session.commit()
            return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/excluirAgendamento/<int:id>', methods=['POST', 'GET'])
@login_required
def excluirAgendamento(id):
    agendamento = Agendamentos.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/servicos', methods=['GET', 'POST'])
@login_required
def servicos():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        descricao = request.form['descricao']

        novo_servico = Servico(nome=nome, preco=preco, descricao=descricao)
        db.session.add(novo_servico)
        db.session.commit()
        return redirect(url_for('servicos'))
    return render_template('cadastreServico.html', servicos=servicos)

@app.route('/unirAgendamentos/<int:id1>/<int:id2>', methods=['POST'])
@login_required
def unirAgendamentos(id1, id2):
    # Obter os dois agendamentos
    agendamento1 = Agendamentos.query.get_or_404(id1)
    agendamento2 = Agendamentos.query.get_or_404(id2)

    # Verificar qual é o mais recente
    if agendamento1.data > agendamento2.data:
        mais_recente = agendamento1
        mais_antigo = agendamento2
    else:
        mais_recente = agendamento2
        mais_antigo = agendamento1

    # Unir os serviços
    for servico in mais_antigo.servicos:
        if servico not in mais_recente.servicos:
            mais_recente.servicos.append(servico)

    # Excluir o agendamento mais antigo
    db.session.delete(mais_antigo)

    # Salvar as alterações
    try:
        db.session.commit()
        flash('Agendamentos unidos com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao unir agendamentos: {str(e)}', 'error')

    return redirect(url_for('home'))

    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)