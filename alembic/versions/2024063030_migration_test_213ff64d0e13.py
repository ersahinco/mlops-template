"""Migration Test

Revision ID: 213ff64d0e13
Revises: da1f831976ba
Create Date: 2024-06-30 12:30:58.189436

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "213ff64d0e13"
down_revision = "da1f831976ba"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "query_results", sa.Column("timestamp", sa.DateTime(), nullable=False)
    )
    op.create_index(
        op.f("ix_query_results_timestamp"), "query_results", ["timestamp"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_query_results_timestamp"), table_name="query_results")
    op.drop_column("query_results", "timestamp")
    # ### end Alembic commands ###
