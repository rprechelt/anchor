##
# ##
# anchor
#
# @file
# @version 0.0.1

# our testing targets
.PHONY: tests flake black isort all

all: mypy isort black flake tests

tests:
	python -m pytest --cov=anchor tests

flake:
	python -m flake8 anchor

black:
	python -m black -t py37 anchor tests

isort:
	python -m isort --atomic -rc -y anchor tests

mypy:
	python -m mypy anchor

# end
