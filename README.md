# lunar-real-estate

## Installation 
Clone the repository:

```sh
$ git clone https://github.com/madisongrams/lunar-real-estate.git
$ cd lunar-real-estate
```

Make sure you have Python >= 3.11 and pip >= 23.2 installed. 
```sh
$ python --version
$ pip --version
```

Create virtual environment and run it
```sh
$ python -m venv lunar
$ source lunar/bin/activate
```

Install redis.
- [Linux](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/)
- [Windows](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/)
- [MacOS](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) 

Start redis server (if you didn't in previous step)
```sh
$ redis-server
```

You can verify redis is up and running with the `redis-cli` command.
```sh
$ redis-cli ping
```

Then install the dependencies:

```sh
$ cd lunar/health_apis
$ pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies, you can apply migrations for the first time.

```sh
$ python manage.py migrate
```

Now you can run the application!

## Running the application
To start the server:
```sh
$ python manage.py runserver
```

Then open 2 more terminal instances navigate to the git repository.
Make sure to activate venv for each.

```sh
$ source lunar/bin/activate
$ cd lunar/health_apis
```

In the first we will start celery beat:
```sh
$ celery -A health_apis.celery beat -l INFO
```

In the second, we will start the celery worker:
```sh
$ celery -A health_apis worker -l info
```

With these up and running, you should be able to use the /stats and /health endpoints.

```sh
$ curl http://127.0.0.1:8000/stats/
$ curl http://127.0.0.1:8000/health/
```

## Testing

In the `lunar/health_apis/` directory, run:

```sh
$ python manage.py test
```
