"""add all_rewies

Revision ID: 26e6ab010f53
Revises: 5a37b4286677
Create Date: 2025-07-02 10:00:11.254778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26e6ab010f53'
down_revision: Union[str, Sequence[str], None] = '5a37b4286677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
