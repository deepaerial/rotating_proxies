# Rotating Proxies

This project is a simple script that checks proxies from file.

* Python 3.11
* [Poetry](https://python-poetry.org/) 

## Installation
Run command below to install the project and its dependencies:
```shell
$ poetry install
```

## Setting up pre-commit hooks
Run command below to setup pre-commit hooks:
```shell
$ poetry run pre-commit install
```

## Running script
Save proxies in a file named `proxies.json` in the root directory of the project from https://proxyscrape.com/free-proxy-list.
To run the script, use the command below:
```shell  
$ poetry run python rotating_proxies
```
