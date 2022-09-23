import setuptools

setuptools.setup(
    name='naptan',
    version='0.1.0',
    url='https://github.com/mullinscr/naptan',
    author='Callum Mullins',
    author_email='mullinscr@gmail.com',
    description='',
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    install_requires=[
        'typing; python_version < "3.5"',
        'attrs',
        'pandas',
        'importlib_resources'
    ],
    classifiers=[
        'Programming Language :: Python :: 3'
    ]
)
