About
=====

Basic ctags auto update plugin for Neovim.

Makes use of neovims async plugin API, so non blocking.

Will not use some checks but lookup the whole path to find tags file.

Requirements
============

- Python3

TODO
====

* Provide configuration through vim

  * ctags binary to use

  * Tags file name to use

  * Logging / Debugging

* Handle possible issues with ctags execution
