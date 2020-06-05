#!/usr/bin/env python3
import os
import os.path as op
import shutil

# the directory where we store showers
SHOWER_DIR = f"{op.join(op.dirname(__file__), 'showers')}"

# setup the environment before importing anchor
os.environ["AIRES_RUN_DIR"] = SHOWER_DIR

import anchor  # noqa:


def delete_showers() -> None:
    """
    Delete any created test showers.
    """

    # get a list of directories inside the shower dir
    dirs = os.listdir(SHOWER_DIR)

    # delete all the showers
    for d in dirs:
        shutil.rmtree(op.join(SHOWER_DIR, d))


def test_create_direct() -> None:
    """
    Test that I can create a direct shower.
    """

    # check that I can create a shower
    sim = anchor.create_direct(
        "anchor_test_direct_shower",
        "proton",
        15.0,
        0.0,
        0.0,
        0.0,
        0.0,
        ground=1.0,
        thinning=1e-1,
        restart=True,
    )

    # run the shower
    sim.run()

    # and delete the evidence
    delete_showers()


def test_create_reflected() -> None:
    """
    Test that I can create a reflected shower.
    """

    # check that I can create a shower
    sim = anchor.create_reflected(
        "anchor_test_reflected_shower",
        "proton",
        15.0,
        0.0,
        0.0,
        0.0,
        0.0,
        ground=1.0,
        thinning=1e-1,
        restart=True,
    )

    # run the shower
    sim.run()

    # and delete the evidence
    delete_showers()
