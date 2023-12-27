************
Installation
************
::

  > pip install adapya-entirex

This installs the *adapya-entirex* with the Python package installer from
the Python Package Index web site.

A required package is adapya.base which will be also installed by pip.


Or to install from a zip file (similarly for tar file)::

  > pip install adapya-entirex-1.3.0.zip


.. note::
   If your local internet is protected by a http proxy you may need to set
   the HTTP\_PROXY environment variable before running pip::

       SET HTTP_PROXY=http://<httpprox.your-local.net>:<httpprox-port>

   Not setting it may result in time out operations.


Prerequisites
=============

Before installing adapya ensure the following:

- Python is available on the platform.

  adapya-entirex supports the Python versions 2.7 or 3.5 and higher

- EntireX V9.0 or higher

- Alternatively install the EntireX mini-runtime

  On Windows this file can be found in the EntireX/Etc/ folder.

The broker interface is loaded as DLL/shared library

- for Windows verify that the directory that contains broker.dll (64 bit) or
  broker32.dll is in the PATH. E.g. ::

    C:/Program Files/Common Files/Software AG  for 64 bit
    C:/Program Files (x86)/Common Files/Software AG for 32 bit

- on Linux the shared library libbroker.so is loaded


.. note:: For users starting with Python a recommended read is the short Python
   Tutorial available with function key F1 in the IDLE Python GUI or at
   `<https://docs.python.org/3/tutorial/index.html>`_

