import os
import os.path as op

# the directory where we store showers
SHOWER_DIR = f"{op.join(op.dirname(__file__), 'showers')}"

# setup the environment before importing anchor
os.environ["AIRES_RUN_DIR"] = SHOWER_DIR

import anchor  # noqa:


def test_anchor_version() -> None:
    """
    Check the anchor version.
    """
    assert anchor.__version__ == "0.0.1"
