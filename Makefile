lint:
	black simio_di && black tests && pylint simio_di

test:
	pytest -vv

deploy:
	python setup.py sdist && twine upload dist/*