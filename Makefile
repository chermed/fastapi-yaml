.PHONY: help init build publish test

SHELL := /bin/bash
DEFAULT_GOAL := help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  init      to initialize the package"
	@echo "  build     to build the package"
	@echo "  publish   to publish the package"
	@echo "  test      to run tests"

# Initialize the package
init:
	python3 -m pip install poetry pre-commit
	poetry install
	pre-commit install

# Build the package
build: init test
	pre-commit autoupdate
	pre-commit run --all-files
	poetry build

# Publish the package
publish:
	poetry publish

# Run tests
test:
	poetry run pytest --cov fastapi_yaml tests/ -s
