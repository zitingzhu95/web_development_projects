"""empty message

Revision ID: 8c30608722fc
Revises: 99a2eec056d0
Create Date: 2022-06-01 05:09:08.203005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c30608722fc'
down_revision = '99a2eec056d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.drop_column('Venue', 'past_shows')
    op.drop_column('Venue', 'upcoming_shows_count')
    op.drop_column('Venue', 'past_shows_count')
    op.drop_column('Venue', 'upcoming_shows')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('upcoming_shows', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('past_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('past_shows', sa.TEXT(), autoincrement=False, nullable=True))
    op.alter_column('Venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###