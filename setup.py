import os
from setuptools import setup, find_packages
from scyllacache import __version__ as package_version


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()
with open(os.path.join(here, 'requirements.txt')) as f:
    requirements = f.read().split()


setup(
    name='scyllacache',
    version=package_version,
    description='ScyllaDB cache for Python picklables',
    long_description=long_description,
    url='https://github.com/marthjod/scyllacache',
    author='marthjod',
    author_email='marthjod@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
)
