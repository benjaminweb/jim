from setuptools import setup, find_packages

setup(
    name='jim',
    packages=['jim'],
    version='0.0.1',
    description='library to retrieve data from German railways',
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
