## pyCirculate

This is a Python wrapper library for interacting with the Anova 2 over Bluetooth LE.

It should work on any Linux with a working BlueZ install.  Most of my testing and development took place on a Raspberry Pi.

## Installation

* Install [bluepy](https://github.com/IanHarvey/bluepy) (it's not currently on pypi and needs to be manually installed).
* `pip install pycirculate`

## Status

*Alpha* -- everything seems to work, but needs more testing.

## TODO

* REST API.
* Testing.


### Credits

I used the [Circulate](https://github.com/neilpa/circulate/) iOS library as a reference implementation for Anova commands.
