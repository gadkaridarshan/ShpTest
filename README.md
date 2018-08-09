# :house: Single Page Application Django 1.9 / Materialize CSS / Fusion Tables


## Installation

### Linux, OS X (shell scripts)

Requirements : Python 3.x, pip
<br>
Optional : DB Browser for SQLite (to check changes in Database)

Create a setenv.sh and a shell.sh based on setenv.example.sh && shell.example.sh

make install will prepare and synchronize database schema based on models and finally run the app

`virtualenv .ve && make install`


Then you should see the App running at :

[localhost:8000](http://localhost:8000)



## Unit testing

Very basic tests

`make test`


## Features implemented

- [x] Single Page Application
- [x] Integration Google Maps
- [x] Integration Fusion Tables
- [x] Integration Django Data Model [Coordinate]
- [x] Events with Data Captured from Front-end (click on Map)
- [x] Reset Data Captured from Front-end (FAB Button)
- [x] Implementing tests


## Credits

Darshan Gadkari

## License

MIT License
