#!/usr/bin/env bash

# This script setups the simulations directory for running simulations
# with MCShower. This unpacks and compiles AIRES and applies ordinary
# ZHAires, reflected ZHAires, and upgoing ZHAires patches.

# stop if anything errors
set -e

# the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# we define a function to do the unpacking
unpack_aires_and_compile () {

    # the first argument is the name of this version
    local version=$1

    # the second argument is the source directory for the ZHAireS patch
    local source=$2

    # the zhaires source directory
    local aires_src=aires_${version}_src    
    local zhaires_src=zhaires_${version}_src

    # unpack the source directory into the current directory
    tar xzf sources/Aires.2-8-4a.tar.gz -C ${DIR}

    # and rename the source
    mv 2-8-4a ${aires_src}

    # unpack the ZHaires version
    tar xf sources/${source}.tar -C ${DIR}

    # and rename the source
    mv ${source} ${zhaires_src}

    # change into the aires directory
    cd ${aires_src}

    # enable the Linux configuration
    sed -i 's/#Platform=Linux/Platform=Linux/g' config

    # create the install directory
    mkdir -p ${DIR}/aires_${version}_install

    # set the install directory
    sed -i "s,AiresRootDir=\${HOME}/aires,AiresRootDir=${DIR}/aires_${version}_install,g" config

    # add our GCC flags to hopefully make things a little faster
    sed -i 's,CFlags="",CFlags="-O3 -march=native -ftree-vectorize",g' config

    # and compile Aires
    ./doinstall 0

    # if we are compiling the reflected version, patch the total time window
    if [ "$version" == "reflected" ]; then
	sed -i "s,maxt=60000,maxt=120000,g" ${DIR}/${zhaires_src}/src/aires/fieldcomm.f
    fi    

    # now copy the files from this ZHAires version
    cp ${DIR}/${zhaires_src}/src/aires/* ${DIR}/${aires_src}/src/aires/
    cp ${DIR}/${zhaires_src}/icfg/* ${DIR}/${aires_src}/icfg/

    # if we are compiling the stratospheric version, copy igrf11
    if [ "$version" == "stratospheric" ]; then
	cp ${DIR}/${zhaires_src}/src/igrf/* ${DIR}/${aires_src}/src/igrf/	
    fi        

    # and redo the compilation now that zhaires is there
    ./doinstall 0

    # if we are compiling the stratospheric version, we also
    # have to compile the special library file for RASPASS.
    if [ "$version" == "stratospheric" ]; then
	SRC=${DIR}/${zhaires_src}/RASPASSprimary/RASPASSprimary.f
	LIBDIR=${DIR}/aires_${version}_install/lib/
	gfortran ${SRC} -o ${DIR}/aires_${version}_install/bin/RASPASSprimary -L${LIBDIR} -lAires
    fi

    # if it's the upgoing version, then add the appropriate special primary dirs
    if [ "$version" == "upgoing" ]; then
	mkdir ${DIR}/aires_${version}_install/special_src
	mkdir ${DIR}/aires_${version}_install/special_bin
    fi

    # change back to the setup directory
    cd ${DIR}

    # check that ZHAires is present in this ZHAires install
    present=`echo Exit | ./aires_${version}_install/bin/Aires | grep -q ZHAireS`
}

# if the first script argument is clean, then delete all the directories
if [ "$1" == "clean" ]; then
    for version in reflected upgoing direct stratospheric; do
	rm -rf aires_${version}_*
	rm -rf zhaires_${version}_*
    done
else
    # otherwise proceed with a build of all the ZHAireS versions
    unpack_aires_and_compile direct ZHAireS-betav28r18c-loopfresnel
    unpack_aires_and_compile reflected ZHAireS-betav28r21-ANITA-reflected-beta0.2-Frcoeffs
    unpack_aires_and_compile upgoing ZHAireS-betav28r18c-Upgoing
    unpack_aires_and_compile stratospheric  ZHAireS-betav28r24-RASPASS
fi
