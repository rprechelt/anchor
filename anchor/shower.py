"""
This module provides functions for easily creating ZHAireS showers
for various geometries and experiments.
"""
import os
import os.path as op
from os.path import dirname, join
from typing import Any, Optional

import igrf12
import zhaires
from zhaires import run_directory


__all__ = ["create_shower", "create_direct", "create_reflected"]

def create_shower(
    name: str,
    particle: str,
    energy: float,
    zenith: float,
    azimuth: float,
    lat: float,
    lon: float,
    date: str = "2016-12-01",
    ground: float = 0.0,
    thinning: float = 1e-6,
    injection: float = 100.0,
    restart: bool = False,
    default: Optional[str] = None,
    program: Optional[str] = None,
    **kwargs: Any,
) -> zhaires.Task:
    """
    Create a new ZHAireS shower with the given event parameters.

    This file loads the `${ANCHOR_DIR}/data/common_default.inp` *before*
    applying any user-specific configuration arguments.

    This is the fundamental simulation function in anchor. The `create_*`
    functions are specific wrappers around `create_shower` that specifically
    load of the included ZHAireS versions.

    If `program` is not provided, then this uses the first `Aires` executable
    found on your PATH. It is recommended to manually set `program` if you
    have multiple Aires/ZHAires version installed.

    Parameters
    ----------
    name: str
        The name of the simulation.
    particle: str
        The ZHAireS string identifying the primary particle type ('proton')
    energy: float
        The cosmic ray energy in log10(eV).
    zenith: float
        The zenith angle of the shower axis in degrees.
    azimuth: float
        The geographic azimuth angle of the shower axis in degrees.
    lat: float
        The latitude of the shower access intersecting the ground in degrees.
    lon: float
        The longitude of the shower access intersecting the ground in degrees.
    date: str
        A date string in the form 'YYYY-MM-DD'
    ground: float
        The ground altitude at the event location in km.
    thinning: float
        The relative thinning level for the simulation (default: 1e-6).
    injection: float
        The injection altitude (in km).
    restart: bool
        If True, don't error if the simulation already exists/already started.
    default: Optional[str]
        The path to a default Aires input file to load before other commands.
    program: Optional[str]
        The path to the ZHAires binary used to create this simulation.


    Returns
    -------
    sim: zhaires.Task
        The created ZHAires simulation that can be run with `sim.run()`.
    """
    # create the simulation directory name
    directory = join(run_directory, f"{name}")

    # create the output directory
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        if restart:
            print("Simulation directory exists. Restarting...")
        else:
            print(e)
            raise ValueError("Simulation already exists. Quitting...")

    # change to the sim directory
    os.chdir(directory)

    # the common defaults file
    common_default = join(
        dirname(dirname(__file__)), *("defaults", "common_default.inp")
    )

    # create a new simulation using the ANITA defaults
    sim = zhaires.Task(program=program, cmdfile=common_default)

    # and load any additional settings from the user provided file
    sim.load_from_file(default)

    # set the name of the task
    sim.task_name(name)

    # specify the output directory
    sim.file_directory(directory, "All")

    # setup the primary particle energy
    sim.primary_particle(particle)
    sim.primary_energy(10.0 ** energy)

    # and the zenith and azimuth information
    sim.primary_zenith(zenith)
    sim.primary_azimuth(azimuth)

    # create the site for this event
    sim.add_site("LatLonAltSite", lat, lon, 1e3 * ground, unit="m")

    # and enable this site for the simulation
    sim.site("LatLonAltSite")

    # get the magnetic field for this site
    B = igrf12.igrf(date, glat=lat, glon=lon, alt_km=ground)

    # and set the magnetic field
    sim.geomagnetic_field(
        B["total"].values[0], B["incl"].values[0], B["decl"].values[0]
    )

    # setup the thinning
    sim.thinning_energy(thinning, relative=True)

    # set the injection altitude
    sim.injection_altitude(injection)

    # and return the simulation
    return sim


def create_reflected(*args: Any, **kwargs: Any) -> zhaires.Task:
    """
    Create a reflected shower using the `reflected_default.inp` file
    and using the reflected ZHAireS version compiled by anchor.

    This is a wrapper around `create_shower`. See the documentation
    for `create_shower` for information on the arguments.
    """

    # make sure default, and program are not in kwargs
    if "default" in kwargs.keys():
        raise ValueError(f"Cannot overide `default` file in create_reflected.")
    if "program" in kwargs.keys():
        raise ValueError(f"Cannot overide `program` in create_reflected.")

    # the location of the ZHAires default input file
    default = join(dirname(dirname(__file__)), *("defaults", "reflected_default.inp"))

    # if program exists, use that name
    name = "AiresQ" if kwargs.get("model") == "AiresQ" else "Aires"

    # and the location of the corresponding Aires binary
    program = join(
        dirname(dirname(__file__)), *("aires", "aires_reflected_install", "bin", name)
    )

    # check that the program exists
    if not op.exists(program):
        raise ValueError(f"Unable to find {program}")

    # and then call create_shower with the given default card
    return create_shower(
        *args, program=program, default=default, **kwargs
    )  # type: ignore


def create_direct(*args: Any, **kwargs: Any) -> zhaires.Task:
    """
    Create a direct shower using the `direct_default.inp` file
    and using the direct ZHAireS version compiled by anchor.

    This is a wrapper around `create_shower`. See the documentation
    for `create_shower` for information on the arguments.
    """

    # make sure default, and program are not in kwargs
    if "default" in kwargs.keys():
        raise ValueError(f"Cannot overide `default` file in create_direct.")
    if "program" in kwargs.keys():
        raise ValueError(f"Cannot overide `program` in create_direct.")

    # the location of the ZHAires default input file
    default = join(dirname(dirname(__file__)), *("defaults", "direct_default.inp"))

    # and the location of the corresponding Aires binary
    program = join(
        dirname(dirname(__file__)), *("aires", "aires_direct_install", "bin", "Aires")
    )

    # check that the program exists
    if not op.exists(program):
        raise ValueError(f"Unable to find {program}")

    # and then call create_shower with the given default card
    return create_shower(
        *args, program=program, default=default, **kwargs
    )  # type: ignore


def create_stratospheric(
    name: str,
    particle: str,
    energy: float,
    zenith: float,
    azimuth: float,
    lat: float,
    lon: float,
    ground: float = 0.0,
    height: float = 38.0,
    thinning: float = 1e-6,
    restart: bool = False,
    **kwargs: Any,
) -> zhaires.Task:
    """
    Create a new ZHAireS simulation of a stratospheric CR event
    with a given set of parameters.

    This uses the custom RASPASS variant of ZHAires and is still
    in *ALPHA* and is not for wide-spread usage.

    Do not use without contacting @rprechelt first.

    Parameters
    ----------
    name: str
        The name of the simulation.
    particle: str
        The ZHAireS string identifying the primary particle type.
    energy: float
        The cosmic ray energy in log10(eV).
    zenith: float
        The zenith angle of the shower axis in degrees.
    azimuth: float
        The geographic azimuth angle of the shower axis in degrees.
    lat: float
        The latitude of the shower access intersecting the ground in degrees.
    lon: float
        The longitude of the shower access intersecting the ground in degrees.
    ground: float
        The ground altitude at the event location in km.
    height: float
        The height (in km) that the trajectory crosses the z-axis.
    thinning: float
        The relative thinning level for the simulation (default: 1e-6).
    restart: bool
        If True, attempt to restart a simulation with the same name.

    Returns
    -------
    sim: zhaires.Task
        The created ZHAires simulation that can be run with `sim.run()`.
    """

    # the location of the ZHAires default input file
    default = join(
        dirname(dirname(__file__)), *("defaults", "stratospheric_default.inp")
    )

    # if program exists, use that name
    pname = "AiresQ" if kwargs.get("model") == "AiresQ" else "Aires"

    # the binary directory for the stratospheric ZHAireS version
    bindir = join(
        dirname(dirname(__file__)), *("aires", "aires_stratospheric_install", "bin")
    )

    # and the location of the corresponding Aires binary
    program = join(bindir, pname)

    # create the simulation directory name
    directory = join(run_directory, f"{name}")

    # create the output directory
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        if restart:
            print("Simulation directory exists. Restarting...")
        else:
            print(e)
            raise ValueError("Simulation already exists. Quitting...")

    # change to the sim directory
    os.chdir(directory)

    # create a new simulation using the ANITA defaults
    sim = zhaires.Task(program=program, cmdfile=default)

    # the common defaults file
    common_default = join(
        dirname(dirname(__file__)), *("defaults", "common_default.inp")
    )

    # create a new simulation using the ANITA defaults
    sim = zhaires.Task(program=program, cmdfile=common_default)

    # and load any additional settings from the user provided file
    sim.load_from_file(default)

    # set the name of the task
    sim.task_name(name)

    # specify the output directory
    sim.file_directory(directory, "All")

    # we must specify the path to the RASPASS binary
    # that creates the special particles
    raspass = join(bindir, "RASPASSprimary")

    # and create the three special primary definitions
    for particle in ["Proton", "Iron", "Electron"]:
        sim(f"AddSpecialParticle RASPASS{particle} {raspass} {particle}")

    # get the name of RASSPAS primary
    if particle.lower() == "proton":
        special = "RASPASSProton"
    elif particle.lower() == "iron":
        special = "RASPASSIron"
    elif particle.lower() == "electron":
        special = "RASPASSElectron"
    else:
        msg = (
            f"stratospheric showers are only supported "
            "for 'proton', 'iron', and 'electron' primaries."
        )
        raise ValueError(msg)

    # setup the primary particle energy to be the special RASPASS particle
    sim.primary_particle(special)
    sim.primary_energy(10.0 ** energy)

    # and the zenith and azimuth information - for stratospheric,
    # we take the complement of the zenith
    sim.primary_zenith(180.0 - zenith)
    sim.primary_azimuth(azimuth)

    # create the site for this event
    sim.add_site("LatLonAltSite", lat, lon, 1e3 * ground, unit="m")

    # and enable this site for the simulation
    sim.site("LatLonAltSite")

    # setup the thinning
    sim.thinning_energy(thinning, relative=True)

    # and set the height at which the particle cross the z-axis
    sim.read_cmd(f"SetGlobal RASPASSHeight {height*1e3:.2f}")

    # warn the users since this is still alpha
    print(f"WARNING: create_stratospheric is still alpha and not recommended for use.")

    # and return the simulation
    return sim
