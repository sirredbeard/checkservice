# Check Service

This project uses Python3, [Flask](http://flask.pocoo.org/), [Bootstrap](https://getbootstrap.com), and [py3270](https://pypi.org/project/py3270/) to provide a web interface that queries a municipal z/OS IBM mainframe.

Depedendecies:

$ pip3 install flask wtforms py3720 -U
$ sudo apt-get install s3720 -y

Configuration:

Set mainframe address, username, and password in `credentials.py.ex` and rename to `credentials.py`.

Made using tools:

[WLinux](https://github.com/WhitewaterFoundry/WLinux)
[Code](https://code.visualstudio.com/download)