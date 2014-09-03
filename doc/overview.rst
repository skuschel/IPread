
Overview
==================================

There are currently 2 ways of using this package as shown here.

Stand-alone command-line-interface
----------------------------------

The CLI can be used for a fast preview of image plate files. The following documentation is shown by running `ipread -h`:

.. program-output:: ../ipread.py -h

Assuming, that all `.inf` files (together with
their `.img` pendants) in the current directory are multiple scans of the same
image plate, the following command would try to create a single HDR Image out
of them and save it as `output.png`.

.. code-block:: bash

   ipread *.inf -s output.png


Using the functionality in your python software
-----------------------------------------------

The `ipread` module can also be imported as a package via

.. code-block:: python

   import ipread

Please see :ref:`ipread` for further documentation.
