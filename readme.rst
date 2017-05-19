About
=====

Basic ctags auto update plugin for Neovim.

Makes use of neovims async plugin API, so non blocking.

Will not use some checks but lookup the whole path to find tags file.

Requirements
============

- Python3

- Neovim

Installation
============

See https://github.com/neovim/python-client/#installation and:

    You need to run :UpdateRemotePlugins in nvim for changes in the specifications to have effect. For details see :help remote-plugin in nvim.

Options
=======

All options are set through::

    let g:neotags_option_name = value

The following options are available:

- ``let g:neotags_tags_filename = "tags"``
   Defines which file name the generated tags file has.

- ``let g:neotags_ctags_cmd = "ctags"``
   Defines the binary to use for generation.

- ``let g:neotags_logging = 0``
   Defines whether to log anything to vims messages.

Development
===========

Install dependencies:

- ``pip install pyfakefs``

Run tests:

``cd rplugin && python -m unittest test.test_neotags``
