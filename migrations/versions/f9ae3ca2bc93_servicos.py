from alembic import op
import sqlalchemy as sa

def upgrade():
    services_table = sa.table('servico',
        sa.Column('id', sa.Integer),
        sa.Column('nome', sa.String(100)),
        sa.Column('descricao', sa.Text)
    )

    op.bulk_insert(services_table,
        [
            {'nome': 'Corte de Cabelo', 'descricao': 'Corte profissional'},
            {'nome': 'Barba', 'descricao': 'Aparação e modelagem'},
            {'nome': 'Manicure', 'descricao': 'Cuidados com as unhas'},
            {'nome': 'Pedicure', 'descricao': 'Cuidados com os pés'},           
            {'nome': 'Maquiagem', 'descricao': 'Aplicação de maquiagem profissional'},
            {'nome': 'Design de Sobrancelhas', 'descricao': 'Modelagem e correção de sobrancelhas'},
            {'nome': 'Escova', 'descricao': 'Alisamento e modelagem do cabelo'}
        ]
    )

def downgrade():
    op.execute("DELETE FROM servico")  # Remove todos os serviços