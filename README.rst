This package is a client-side interface to Mozilla's system inventory
application.

Installation
------------

Mozinventory is not yet released, so it must be installed directly from the
version-control repository, meaning that you get the latest and greatest.

You can install this application in one of two ways.  The first is easier, but
will require root access, and will leave mozinventory files mingled with files
installed by your OS.  The second is a bit more work, but is more isolated and
does not require root access.

Root Installation
=================

Become root, and make sure that the ``git`` and ``pip`` commands for are
available.  Then run::

    # pip install git+git://github.com/rtucker-mozilla/mozinventory.git

To upgrade to a newer version::

    # pip install -U git+git://github.com/rtucker-mozilla/mozinventory.git

The ``mozinventory`` script should now be in your path::

    $ mozinventory --help-commands

User Installation
=================

The Python utility ``virtualenv`` allows you to create an isolated environment
for installation of applications like ``mozinventory``.  You will need ``git``
and ``virtualenv`` installed for this to work -- both should be available from
your package management system.

The ``~/mozinventory`` directory below can be changed to suit your own desires.

First, create a virtualenv::

    $ virtualenv ~/mozinventory

Now, install ``mozinventory`` into that virtualenv, as was done for the root
install above, but using pip from the virtualenv::

    $ ~/virtualenv/bin/pip install git+git://github.com/rtucker-mozilla/mozinventory.git

As above, add the ``-U`` flag to upgrade later.  The ``mozinventory`` script
will be located in the virtualenv.  You can add this directory to your
``$PATH``, create a symlink, or just use the explicit path::

    $ ~/virtualenv/bin/mozinventory --help-commands

Configuration
=============

Configuration is in ~/.mozinventoryrc.  This file must have mode 0700.  It is
an ini-style file supporting the following arguments:

[api]
url - the base API URL

[auth]
username - for Mozilla, the long LDAP form
password - password for username

[debug]
api - set to '1' to debug the inventory API interface

Usage
-----

Refer to the ``--help-commands`` command for usage information.
