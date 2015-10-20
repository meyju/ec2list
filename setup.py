# Setup ec2list

from setuptools import setup, find_packages
from codecs import open
from os import path

from ec2list import VERSION

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ec2list',

    version=VERSION,

    description='Lists your ec2 instances in the command line.',
    long_description=long_description,

    url='https://github.com/meyju/ec2list',

    author='Julian Meyer',
    author_email='jm@julianmeyer.de',

    license='GPL',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',

        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='aws amazon web services ec2 list admin',

    zip_safe=True,

    packages=find_packages(exclude=['build', '_docs', 'templates']),
    install_requires=['boto>=2.36.0', 'configparser'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'ec2list=ec2list.ec2list:main',
        ],
    },
)
