# Check Service

This project uses Python3, [Flask](http://flask.pocoo.org/), [Flask Limiting](https://flask-limiter.readthedocs.io/en/stable/) [Bootstrap](https://getbootstrap.com), and [py3270](https://pypi.org/project/py3270/) to provide a web interface that queries a municipal z/OS IBM mainframe.

**Features:**

- Encrypted connection to mainframe.
- Rate limiting.
- Error handling.
- Optional HTTPS using Certbot and Gunicorn.

**Depedendecies:**

- `$ sudo apt-get install git python3 python3-pip s3270 -y` Note: s3270 requires non-free repo to be enabled.
- `$ pip3 install flask flask_limiter wtforms py3270 pyopenssl gunicorn python3-dateutil -U`

**Installation:**

- `$ git clone https://github.com/sirredbeard/checkservice && cd checkservice`

**Configuration:**

- Set mainframe address, username, and password in `credentials.py.ex` and rename to `credentials.py`:
    - `$ nano credentials.py.ex`
    - `$ mv credentials.py.ex credentials.py`

**Running:**

- `$ python3 app.py`

**With HTTPS:**

- Set debug to False at line 11 in production environments.
- Generate certs with [certbot](https://certbot.eff.org/) and place in ./certs/cert.pem and ./certs/privkey.pem.
- Set ip address and portnumber in `run.sh.ex` and rename to `run.sh`:
    - `$ nano run.sh.ex`
    - `$ mv run.sh.ex run.sh`
- `$ bash run.sh`

**Made using tools:**

- [WLinux](https://github.com/WhitewaterFoundry/WLinux)
- [Code](https://code.visualstudio.com/download)