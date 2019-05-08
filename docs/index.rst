.. xcmds documentation master file, created by
   sphinx-quickstart on Wed May  8 11:43:51 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to xcmds's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. automodule:: xcmds.xcmds
   :members:

Example
========
example.py::

   from xcmds.xcmds import xcmds
   from pprint import pprint as print


   def func(a=1, b=2):
       print(a*b)


   def func2(a='x', b=3):
       print([a]*b)


   if __name__ == '__main__':
       xcmds(locals(), exclude=['print'])

Now all functions in example.py are ready to be called with command line,
eg. Type in terminal::

   python example.py func -a 100


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
