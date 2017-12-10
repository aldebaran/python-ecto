Python packaging for ecto and open-source ecto cells

How to compile
==============

You need to use qibuild and a qibuild toolchain to be able to compile this
package. Your toolchain must contain at least the development files of the
following libraries:

Boost
OpenCV3
Python

Then download all the sources required and compile the project by running::

    make qibuild_workspace
    make ecto

