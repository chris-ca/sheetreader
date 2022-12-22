install:
	poetry install

format:
	black sheetreader/*.py

lint:
	pylint --disable=R,C ./sheetreader

test:
	python -m pytest -v tests/

test_release:
	poetry publish --build -r testpypi

all: install lint test
