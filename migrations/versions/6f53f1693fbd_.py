"""empty message

Revision ID: 6f53f1693fbd
Revises: 9185a82df7f1
Create Date: 2020-01-11 12:42:23.456389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f53f1693fbd'
down_revision = '9185a82df7f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job_seeker', sa.Column('current_company', sa.String(length=200), nullable=True))
    op.add_column('job_seeker', sa.Column('current_package', sa.String(length=200), nullable=True))
    op.add_column('job_seeker', sa.Column('name', sa.String(length=50), nullable=True))
    op.add_column('job_seeker', sa.Column('place', sa.String(length=200), nullable=True))
    op.add_column('job_seeker', sa.Column('role', sa.String(length=200), nullable=True))
    op.add_column('job_seeker', sa.Column('updated', sa.Boolean(), nullable=True))
    op.add_column('recruiter', sa.Column('name', sa.String(length=50), nullable=True))
    op.add_column('recruiter', sa.Column('updated', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recruiter', 'updated')
    op.drop_column('recruiter', 'name')
    op.drop_column('job_seeker', 'updated')
    op.drop_column('job_seeker', 'role')
    op.drop_column('job_seeker', 'place')
    op.drop_column('job_seeker', 'name')
    op.drop_column('job_seeker', 'current_package')
    op.drop_column('job_seeker', 'current_company')
    # ### end Alembic commands ###
