"""user Contry details added in users table

Revision ID: 8f44af6842bf
Revises: b04cd740af4e
Create Date: 2024-08-12 19:13:42.193826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f44af6842bf'
down_revision: Union[str, None] = 'b04cd740af4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('otp', sa.String(length=61), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'otp')
    # ### end Alembic commands ###
