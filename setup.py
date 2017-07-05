from setuptools import setup, find_packages

setup(
    name='jim',
    version='0.0.1',
    description='library to retrieve data from German railways',
    url='https://bitbucket.org/hyllos/jim',
    author='Benjamin Weber',
    author_email='mail@bwe.im',
    license='MIT',
    packages=find_packages(exclude=['tests']),
)
