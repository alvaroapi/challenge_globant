#!/bin/bash
set -e

python manage.py migrate --noinput

exec "$@"