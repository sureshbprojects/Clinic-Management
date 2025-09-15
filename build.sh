set -o errexit

pip install -r requirments.txt

python manage.py migrate

python manage.py collectstatic --no-input

