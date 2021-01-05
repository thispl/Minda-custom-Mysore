# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in minda_custom/__init__.py
from minda_custom import __version__ as version

setup(
	name='minda_custom',
	version=version,
	description='Payroll',
	author='TeamPRO',
	author_email='barathprathosh@groupteampro.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
