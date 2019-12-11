#!/usr/bin/env python
# requires Python V2.6 or higher
from __future__ import print_function          # PY3

import os,sys

try:
    from setuptools import setup
except:
    print('no setuptools found, trying distutils.core')
    from distutils.core import setup  # noqa

pver=sys.version[0]
prel=sys.version[2]

print('Active runtime:',sys.version, pver, prel)

extra = {}
#   extra['install_requires'] = ['uuid']

install_requires = [
    'adapya.base>=1.0.0',
]

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(  name='adapya.entirex',
    version='1.0.1',
    author='mmueller',
    author_email='mm@softwareag.com',
    description='adapya.entirex - Software AG webMethods EntireX Broker API for Python',
    license='Apache License 2.0',
    url='http://tech.forums.softwareag.com/viewforum.php?f=171&C=11',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
         'Intended Audience :: Developers',
         'Intended Audience :: Devops',
         'Natural Language :: English',
         'Operating System :: Microsoft :: Windows',
         'Operating System :: POSIX :: AIX',
         'Operating System :: POSIX :: HP-UX',
         'Operating System :: POSIX :: SunOS/Solaris',
         'Operating System :: POSIX :: Linux',
         'Operating System :: IBM :: z/OS',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3.5',
         'Programming Language :: Python :: 3.6',
         'Programming Language :: Python :: 3.7',
         'Topic :: Database',
         'Topic :: Devops',
         ],
    keywords='softwareag webMethods EntireX Broker',
    long_description=README,
    zip_safe=False,
    scripts = ['adapya/entirex/cmdinfo.py',],
    packages=['adapya', 'adapya.entirex', ],
    install_requires=install_requires,
    namespace_packages=['adapya'],
    #extras_require={ 'dev': [ 'coverage','nose','pytest','pytest-pep8','pytest-cov' ]},

    platforms='any',
    **extra
)
