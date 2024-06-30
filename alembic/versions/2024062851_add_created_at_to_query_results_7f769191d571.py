"""Add created_at to query_results

Revision ID: 7f769191d571
Revises: 88d16987ca9e
Create Date: 2024-06-28 21:51:47.954070

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "7f769191d571"
down_revision = "88d16987ca9e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "query_records",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.drop_column("query_records", "create_time")
    op.drop_column("query_results", "create_time")
    op.add_column(
        "refresh_token",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.drop_column("refresh_token", "create_time")
    op.add_column(
        "user_account",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.drop_column("user_account", "create_time")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user_account",
        sa.Column(
            "create_time",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("user_account", "created_at")
    op.add_column(
        "refresh_token",
        sa.Column(
            "create_time",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("refresh_token", "created_at")
    op.add_column(
        "query_results",
        sa.Column(
            "create_time",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "query_records",
        sa.Column(
            "create_time",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("query_records", "created_at")
    # ### end Alembic commands ###
