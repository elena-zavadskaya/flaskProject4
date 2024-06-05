"""Добавление модели UserLibrary

Revision ID: 26b73d8a5d09
Revises: 93ff5e8973ef
Create Date: 2024-05-22 23:55:14.716667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26b73d8a5d09'
down_revision = '93ff5e8973ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('author', sa.String(length=128), nullable=False),
    sa.Column('cover', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_libraries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('book_id', sa.String(length=60), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('authors', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_libraries')
    op.drop_table('books')
    # ### end Alembic commands ###
