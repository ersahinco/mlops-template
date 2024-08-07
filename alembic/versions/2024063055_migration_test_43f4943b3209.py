"""Migration Test

Revision ID: 43f4943b3209
Revises: cda54004f235
Create Date: 2024-06-30 13:55:51.861278

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "43f4943b3209"
down_revision = "cda54004f235"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("refresh_token", sa.Column("exp", sa.BigInteger(), nullable=False))
    op.add_column(
        "refresh_token", sa.Column("user_id", sa.Uuid(as_uuid=False), nullable=False)
    )
    op.create_foreign_key(
        None,
        "refresh_token",
        "user_account",
        ["user_id"],
        ["user_id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "refresh_token", type_="foreignkey")
    op.drop_column("refresh_token", "user_id")
    op.drop_column("refresh_token", "exp")
    # ### end Alembic commands ###
