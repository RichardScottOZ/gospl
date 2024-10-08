.. _getting_started:

===============
Getting started
===============


Python version support
----------------------

goSPL supports versions :mod:`3.9` to :mod:`3.12` of Python.

Installation instructions
-------------------------

The easiest way to start using goSPL is to install it from its Docker image, a cross platform distribution for data analysis and scientific computing. This is the recommended installation method for most users.

Instructions for installing it via Anaconda or from source are also provided.


.. grid:: 1 1 2 2
    :gutter: 2 3 4 4

    .. grid-item-card::
        :img-top: ../_static/docker.svg
        :text-align: center

        **Docker image**
        ^^^

        Virtualisation with `Docker container <https://hub.docker.com/r/geodels/gospl>`_ provides a simple approach for running goSPL simulation.

        +++

        .. button-ref:: installDocker
            :color: secondary
            :click-parent:

            Install via Docker

    .. grid-item-card::
        :img-top: ../_static/anaconda.svg
        :text-align: center

        **Conda environment**
        ^^^

        For Anaconda users, an environment with specific collection of conda packages and goSPL dependencies is available.

        +++

        .. button-ref:: installConda
            :color: secondary
            :click-parent:

            Install via Conda


    .. grid-item-card::
        :img-top: ../_static/python.svg
        :text-align: center

        **Install from source**
        ^^^

        goSPL can also be installed directly from source but this requires installation of all other dependencies. 

        +++

        .. button-ref:: installSrc
            :color: secondary
            :click-parent:

            Learn more

    .. grid-item-card::
        :img-top: ../_static/hpc.svg
        :text-align: center

        **Install on HPC**
        ^^^

        goSPL installation on High Performance computers. 

        +++

        .. button-ref:: installHPC
            :color: secondary
            :click-parent:

            Learn more

.. toctree::
    :maxdepth: 2
    :hidden:

    installDocker
    installConda
    installSrc
    installHPC
