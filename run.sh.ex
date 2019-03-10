#!/bin/bash
gunicorn -w 4 --bind ipaddress:portnumber --certfile=./certs/cert.pem --keyfile=./certs/privkey.pem app:app