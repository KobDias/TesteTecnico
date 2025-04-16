# Sistema de Agendamentos - Cabeleleila Leila

Este é um sistema de agendamentos desenvolvido em Flask para gerenciar clientes, serviços e agendamentos de forma eficiente.

## Funcionalidades

- Cadastro e login de clientes.
- Criação, edição e cancelamento de agendamentos.
- Gerenciamento de serviços.
- Painel administrativo para gerenciar clientes, agendamentos e serviços oferecidos.
- Sistema de autenticação com controle de acesso para administradores e clientes.

## Tecnologias Utilizadas

- **Backend**: Flask, Flask-Login, Flask-SQLAlchemy
- **Banco de Dados**: SQLite
- **Frontend**: Bootstrap 4
- **Outras Dependências**: SQLAlchemy, Jinja2

## Estrutura do Projeto

```
TesteTecnico/
    .gitignore
    app.py
    db.py
   instance/
       cabeleleila.db
    models.py
    README.md
    requirements.txt
    servico.py
    templates/
        cadastreCliente.html
        cadastreServico.html
        cadastro.html
        criarAgendamento.html
        editarAgendamento.html
        header.html
        index.html
        login.html
```

## Pré-requisitos

- Python 3.10+ instalado
- Git instalado
- pip (gerenciador de pacotes do Python)

# Como Executar o Projeto

## Passo a Passo

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/KobDias/TesteTecnico.git
   cd TesteTecnico
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```


5. **Execute o servidor**:
   ```bash
   flask run
   ```

6. **Acesse a aplicação**:

   Abra no navegador:
      
   ```
   http://127.0.0.1:5000/
   ```
