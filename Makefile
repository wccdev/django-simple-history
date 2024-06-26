all: init docs clean test

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr dist/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

init:
	pip install "tox>=1.8" coverage

test:
	coverage erase
	tox
	coverage html

docs: documentation

documentation:
	tox -e docs

dist: clean
	pip install -U build
	python -m build
	for file in dist/* ; do gpg --detach-sign -a "$$file" ; done
	ls -l dist

test-release: dist
	pip install -U twine
	gpg --detach-sign -a dist/*
	twine upload -r pypitest dist/*

release: dist
	pip install -U twine
	gpg --detach-sign -a dist/*
	twine upload dist/*

format:
	tox -e format
