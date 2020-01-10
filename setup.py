from setuptools import find_packages, setup

setup(
    name='prude',
    version='0.1',
    packages=find_packages(),
    url='http://greatdeceiver.com/prude.html',
    license='MIT',
    author='jim',
    author_email='jim.smith@gmail.com',
    description='UK Gov styled http only SQL editor',
    install_requires=[
        'flask',
    ],
)
