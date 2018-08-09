# Prepare the application [dependencies, database]
install:
	pip install -r requirements.txt
	python mysite/manage.py makemigrations
	python mysite/manage.py migrate --run-syncdb
	# Set environment variables (SECRET)
	./setenv.sh

shell:
	./shell.sh
