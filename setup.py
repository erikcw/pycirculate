from setuptools import setup, find_packages


setup(
    name="pycirculate",
    version="0.1.1a1",
    description="A Python wrapper for the Anova 2.",
    long_description="A Python wrapper library for interacting with the Anova 2 over Bluetooth LE on Linux.",
    url="https://github.com/erikcw/pycirculate",
    author="Erik Wickstrom",
    author_email="erik@erikwickstrom.com",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='anova bluetooth bluepy sous vide',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    # bluepy isn't currently on pypi, uncomment as soon as it is available.
    # install_requires=['bluepy'],
)
