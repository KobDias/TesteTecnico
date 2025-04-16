from collections import defaultdict 
# ↑ um tipo especial de array que preenche nulls
from flask import Flask, url_for, render_template, request, redirect, url_for
# ↑ importação do flask e ferramentas para redirecionamento
from db import db
from models import Cliente, Agendamentos, Servico, Estado
# ↑ banco de dados
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# ↑ bibliotecas para login
import hashlib

# configurando o app
app = Flask(__name__)
app.secret_key = "m04H4H4"
lm = LoginManager(app)
lm.login_view = 'login' # se entrar em area em que login_required, vai pra login
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabeleleila.db'
db.init_app(app)

def hash(txt): # função de criptografia básica de senhas
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader # decorador para carregar user
def load_user(id): # pega o id para carregar user
    cliente = db.session.query(Cliente).filter_by(id=id).first()
    return cliente

@app.route('/') # rota home
def home():
    if current_user.is_authenticated: # se logado
        if current_user.is_admin: # se admin
            agendamentos = Agendamentos.query.order_by(Agendamentos.data.asc()) # pega todos os agendamentos
            return render_template('index.html', agendamentos=agendamentos, semanas_com_multiplos={}) 
        else: # se não admin
            # Lógica de avisos de agendamentos na mesma semana
            agendamentos = Agendamentos.query.filter_by(clienteId=current_user.id).order_by(Agendamentos.data.asc()).all()
            agendamentosPendente = Agendamentos.query.filter(Agendamentos.clienteId==current_user.id, Agendamentos.estado == Estado.pendente).order_by(Agendamentos.data.asc()).all()

            agendamentos_por_semana = defaultdict(list) # agendamento por semanas
            for agendamento in agendamentosPendente:
                # por semana
                ano, semana, _ = agendamento.data.isocalendar()
                agendamentos_por_semana[(ano, semana)].append({
                    'id': agendamento.id,
                    'data': agendamento.data,
                    'dia_semana': agendamento.data.strftime('%A'),  # Nome do dia da semana
                    'servicos': agendamento.servicos
                })

            # Filtrar semanas com múltiplos agendamentos
            semanas_com_multiplos = {semana: ags for semana, ags in agendamentos_por_semana.items() if len(ags) > 1}
            return render_template('index.html', agendamentos=agendamentos, semanas_com_multiplos=semanas_com_multiplos) 
    return render_template('index.html', agendamentos=[], semanas_com_multiplos={})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cliente = db.session.query(Cliente).filter_by(email=email, senha=hash(senha)).first() # compara as infos com o banco
        if cliente: # se realmente cliente
            login_user(cliente) # logar
            return redirect(url_for('home'))
        else:
            return "Email ou senha invalidos"
    #GET
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']

        # carrega as informações e criptografa a senha
        novoCliente = Cliente(nome=nome, email=email, telefone=telefone, senha=hash(senha))

        #armazena e salva
        db.session.add(novoCliente)
        db.session.commit()

        login_user(novoCliente) # loga depois do cadastro
        return redirect(url_for('home'))
    #GET
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/agendamentos', methods=['GET', 'POST'])
@login_required # criar agendamentos se logado
def agendamentos():
    if request.method == 'POST':

        # Obter dados do formulário
        dataHora = datetime.strptime(request.form.get('dataHora'), '%Y-%m-%dT%H:%M')
        servicos_ids = request.form.getlist('servicos')

        # verifica se dia passado ou servicos estão vazios
        if dataHora < datetime.now() or servicos_ids==[]:
            return "Não é possivel marcar uma data passada ou deixar de escolher um serviço!"

        if current_user.is_admin: #sendo admin, é preciso especificar o cliente

            clienteInput = request.form.get('cliente')
            cliente = Cliente.query.get(clienteInput) # pega o cliente 

            novoAgendamento = Agendamentos(
                clienteId=cliente.id,
                data=dataHora,
                is_confirmed=True, # se um admin fez, tá confirmado
            )
        else: # não sendo admin, cliente é current_user
            novoAgendamento = Agendamentos(
                clienteId=current_user.id,
                data=dataHora
                # por padrão, is_confirmed é false  
            )
        
        #independente do cliente ou data, servicos precisam ser inseridos
        for servico_id in servicos_ids:
            servico = Servico.query.get(servico_id) # visualiza cada servico checked
            novoAgendamento.servicos.append(servico) # append ao novo agendamento
    
        #salva no banco
        db.session.add(novoAgendamento)
        db.session.commit()

        return redirect(url_for('home'))
    #GET
    todosClientes = Cliente.query.filter_by(is_admin = False).all() # carregar os clientes existentes. Não pode ser admin
    todosServicos = Servico.query.all() # Carregar serviços cadastrados
    return render_template('criarAgendamento.html', servicos=todosServicos, clientes=todosClientes)

@app.route('/editarAgendamento/<int:id>', methods=['GET', 'POST'])
@login_required
def editarAgendamento(id):
    agendamento = Agendamentos.query.get_or_404(id) # recebe o id
    todosServicos = Servico.query.all()  # Todos os serviços disponíveis

    # verificação
    if not current_user.is_admin:
        dataAgendado = agendamento.data
        dataHoje = datetime.now()
        distancia = (dataAgendado - dataHoje).days
        if abs(distancia) < 2: # se o agendamento for em até dois dias, editarAgendamento não abre
            return "Infelizmente, edições só podem ser feitas até dois dias antes do agendamento. Ligue para a Leila em 55555555 para alterações."
    if request.method == 'POST':
        
        # Atualizar os dados do agendamento conforme necessári0

        # recebe hora
        agendamento.data = datetime.strptime(request.form.get('dataHora'), '%Y-%m-%dT%H:%M')

        # converte estado da lista dropdown(string para Enum) e recebe novo estado
        novo_estado = request.form.get('estado')
        agendamento.estado = Estado[novo_estado]

        # recebe os servicos selecionados (strings)
        novoServicos_ids = request.form.getlist('servicos')

        if agendamento.data < datetime.now() or novoServicos_ids==[]:
            return "Não é possivel marcar uma data passada ou deixar de escolher um serviço!"
        else:
            idsAtuais = {s.id for s in agendamento.servicos} # pega os ids dos servicos já em agendamentos
            novos_ids = set(map(int, novoServicos_ids)) # converte para ints
            
            para_remover = idsAtuais - novos_ids  # calcula as diferenças
            for servico_id in para_remover: # remove elas
                servico = Servico.query.get(servico_id)
                if servico:
                    agendamento.servicos.remove(servico)

            para_adicionar = novos_ids - idsAtuais # calcula as diferenças
            for servico_id in para_adicionar: # adiciona elas
                servico = Servico.query.get(servico_id)
                if servico:
                    agendamento.servicos.append(servico)
        try:
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return "Erro"
    #GET
    servicos = Servico.query.all()
    return render_template('editarAgendamento.html', agendamento=agendamento, servicos=servicos, estados=Estado, todos_servicos=todosServicos)

@app.route('/cancelarAgendamento/<int:id>', methods=['GET'])
@login_required
def cancelarAgendamento(id):
    if current_user.is_admin:
        agendamento = Agendamentos.query.get_or_404(id)
        agendamento.estado = Estado.cancelado
    else:
        agendamento = Agendamentos.query.get_or_404(id)
        dataAgendado = agendamento.data
        dataHoje = datetime.now()
        distancia = (dataAgendado - dataHoje).days
        if abs(distancia) < 2:
            return "Infelizmente, cancelamentos só podem ser feitos até dois dias antes do agendamento. Ligue para a Leila em 55555555 para alterações."
        else:
            agendamento.estado = Estado.cancelado
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/unirAgendamentos/<int:id1>/<int:id2>', methods=['POST'])
@login_required
def unirAgendamentos(id1, id2):
    # Obter os dois agendamentos
    agendamento1 = Agendamentos.query.get_or_404(id1)
    agendamento2 = Agendamentos.query.get_or_404(id2)

    #informações dos forms ocultos
    dia1 = request.form.get('dia1')
    dia2 = request.form.get('dia2')

    dias_semana = { # mapeando os dias da semana
        "Monday": 2,
        "Tuesday": 3,
        "Wednesday": 4,
        "Thursday": 5,
        "Friday": 6,
        "Saturday": 7,
        "Sunday": 1
    }

    # Verificar qual é o mais recente
    if dias_semana[dia1] < dias_semana[dia2]:
        mais_recente = agendamento1
        mais_antigo = agendamento2
    else:
        mais_recente = agendamento2
        mais_antigo = agendamento1

    agendamentoUnico = Agendamentos(
        clienteId=current_user.id,
        data=mais_recente.data,
    )
    uniao = mais_recente.servicos + mais_antigo.servicos # unindo os serviços
    # Unir os serviços
    for servico in uniao:
        if servico not in agendamentoUnico.servicos: # evitar duplicatas
            agendamentoUnico.servicos.append(servico)

    

    mais_recente.estado = Estado.cancelado
    mais_antigo.estado = Estado.cancelado

    # Salvar as alterações
    try:
        db.session.add(agendamentoUnico)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return "Erro ao unir agendamentos: " + str(e)

# Apenas ADM

@app.route('/confirmarAgendamento/<int:id>', methods=['GET'])
@login_required
def confirmarAgendamento(id):
    if current_user.is_admin:
        agendamento = Agendamentos.query.get_or_404(id)

        agendamento.is_confirmed = True
        db.session.commit()

        return redirect(url_for('home'))
    else:
        return "Não administrador"

@app.route('/excluirAgendamento/<int:id>', methods=['GET'])
@login_required
def excluirAgendamento(id):
    if current_user.is_admin:
        agendamento = Agendamentos.query.get_or_404(id)

        db.session.delete(agendamento)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return "Você não tem permissão para visualizar essa página"


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

@app.route('/cadastrarCliente', methods=['POST', 'GET']) 
@login_required
def cadastrarCliente():
    if current_user.is_admin:
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form['telefone']
            senha = request.form['senha']

            novo_cliente = Cliente(nome=nome, email=email, telefone=telefone, senha=hash(senha))
            db.session.add(novo_cliente)
            db.session.commit()
            return redirect(url_for('home'))
        #GET
        return render_template('cadastreCliente.html')
    else:
        return "Você não tem permissão para acessar esta página."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar administrador padrão, se não existir
        admin_email = "admin@cabeleleila.com"
        admin = Cliente.query.filter_by(email=admin_email).first()
        if not admin:
            admin = Cliente(
                nome="Administrador",
                email=admin_email,
                telefone="000000000",
                senha=hash("admin123"),  # Senha padrão
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

        # Criar serviços padrão, se não existirem
        servicos_padrao = [
            {"nome": "Corte de Cabelo", "preco": 50.0, "descricao": "Corte profissional de cabelo."},
            {"nome": "Manicure", "preco": 30.0, "descricao": "Manicure completa."},
            {"nome": "Pedicure", "preco": 40.0, "descricao": "Pedicure completa."},
            {"nome": "Escova", "preco": 60.0, "descricao": "Escova modeladora."},
            {"nome": "Design de Sobrancelhas", "preco": 20.0, "descricao": "Design profissional de sobrancelhas."},
            {"nome": "Maquiagem", "preco": 80.0, "descricao": "Maquiagem completa para eventos."}
        ]
        for servico_data in servicos_padrao:
            servico = Servico.query.filter_by(nome=servico_data["nome"]).first()
            if not servico:
                servico = Servico(**servico_data)
                db.session.add(servico)
        db.session.commit()
    app.run(debug=True)