```markdown
# Como Executar o Projeto

## Pré-requisitos
- Python 3.10+ instalado
- Git instalado
- pip (gerenciador de pacotes do Python)

## Passo a Passo

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/KobDias/TesteTecnico.git
   cd TesteTecnico
   ```

2. **Crie um ambiente virtual** (recomendado):
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

5. **Configure o banco de dados**:
   ```bash
   flask db init          # Inicializa migrações (se necessário)
   flask db migrate       # Cria migração
   flask db upgrade       # Aplica migrações ao banco
   ```

6. **Execute o servidor**:
   ```bash
   flask run
   ```

7. **Acesse a aplicação**:
   Abra no navegador:  
   http://localhost:5000

## Dicas
- 🛠️ Para criar um usuário admin, use o Flask Shell:
  ```bash
  flask shell
  >>> from models import Cliente
  >>> admin = Cliente(nome="Admin", email="admin@exemplo.com", senha="senha123")
  >>> db.session.add(admin)
  >>> db.session.commit()
  ```
- 🔧 Se houver um `requirements-dev.txt`, instale dependências de desenvolvimento:
  ```bash
  pip install -r requirements-dev.txt
  ```

✨ **Pronto!** O sistema de agendamentos estará rodando localmente.
```
