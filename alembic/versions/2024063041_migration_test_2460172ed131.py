"""Migration Test

Revision ID: 2460172ed131
Revises: 6ed92e4e3076
Create Date: 2024-06-30 13:41:19.299836

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2460172ed131"
down_revision = "6ed92e4e3076"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_refresh_token_refresh_token", table_name="refresh_token")
    op.drop_table("refresh_token")
    op.drop_index("ix_user_account_email", table_name="user_account")
    op.drop_table("user_account")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_account",
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("email", sa.VARCHAR(length=256), autoincrement=False, nullable=False),
        sa.Column(
            "hashed_password",
            sa.VARCHAR(length=128),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", name="user_account_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_index("ix_user_account_email", "user_account", ["email"], unique=True)
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column(
            "refresh_token", sa.VARCHAR(length=512), autoincrement=False, nullable=False
        ),
        sa.Column("used", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("exp", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_account.user_id"],
            name="refresh_token_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="refresh_token_pkey"),
    )
    op.create_index(
        "ix_refresh_token_refresh_token",
        "refresh_token",
        ["refresh_token"],
        unique=True,
    )
    # ### end Alembic commands ###
