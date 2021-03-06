"""empty message

Revision ID: b8859b2f85a0
Revises: 8b8a1aa1838c
Create Date: 2020-01-10 11:45:40.971876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8859b2f85a0'
down_revision = '8b8a1aa1838c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job_seeker', sa.Column('interested_stack', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('job_seeker', 'interested_stack')
    # ### end Alembic commands ###
