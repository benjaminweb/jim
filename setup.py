from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jim',
    packages=['jim'],
    version='0.0.1',
    description='library to retrieve data from German railways',
    long_description=long_description,
    url='https://bitbucket.org/hyllos/jim',
    author='Benjamin Weber',
    author_email='mail@bwe.im',
    license='MIT',
    install_requires=['pendulum', 'regex', 'requests', 'backoff'],
    extras_require={'test': ['responses']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='bahn train traffic'
)
