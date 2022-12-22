install:
	poetry install

format:
	black sheetreader/*.py

lint:
	pylint --disable=no-member,invalid-name ./sheetreader

test:
	python -m pytest -v tests/

test_release:
	poetry publish --build -r testpypi

all: install lint test
