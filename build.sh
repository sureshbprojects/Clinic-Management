set -o errexit

pip install -r requirments.txt

python manage.py migrate

python manage.py collectstatic --no-input

if [[$CREATE_SUPERUSER]]; 
then
    python manage.py createsuperuser    --no-input
fi