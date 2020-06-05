##
# ##
# anchor
#
# @file
# @version 0.0.1

# our testing targets
.PHONY: tests flake black all

all: mypy black flake tests

tests:
	python -m pytest --cov=anchor tests

flake:
	python -m flake8 anchor

black:
	python -m black -t py37 anchor tests

mypy:
	python -m mypy anchor

# end
