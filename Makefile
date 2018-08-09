# Prepare the application [dependencies, database]
install:
	pip install -r requirements.txt && \
	python manage.py makemigrations && \
	python manage.py migrate --run-syncdb && \
	./setenv.sh

test:
	./test.sh

shell:
	./shell.sh
