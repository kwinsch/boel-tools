#!/usr/bin/env python

from distutils.core import setup

setup(name='boel-lib',
      version='0.2',
      description='boel utils shared libraries',
      author='Kevin Bortis',
      author_email='kevin@bortis.ch',
      url='http://www.bortis.ch',
      packages=['belib', 'belib.format', 'belib.date', 'belib.crypt',
		'belib.contrib', 'belib.contrib.crypt'],
     )
