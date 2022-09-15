.PHONY: notebook docs
.EXPORT_ALL_VARIABLES:
.ONESHELL:

# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

install: 
	@echo "Installing..."
	conda env create -f environment.yaml
	$(CONDA_ACTIVATE) venv
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
	source $(HOME)/.poetry/env
	poetry install
	#@echo "Fixing mistake in libary based on https://github.com/ablab/spades/issues/873"
	#find ./venv/lib/*/site-packages/yaml -name constructor.py -exec sed -i 's/collections.Hashable/collections.abc.Hashable/g' {} \;
	git rm -r --cached 'data/raw'
	git rm -r --cached 'data/processed'
	git rm -r --cached 'data/final'
	git rm -r --cached 'models'

pull_data:
	run dvc pull

setup: install

update_requirements:
	$(CONDA_ACTIVATE) venv
	poetry update

install_packages:
	$(CONDA_ACTIVATE) venv
	poetry install

# run like make poetry_install name="<package_name>"
poetry_install:
	$(CONDA_ACTIVATE) venv
	poetry add $(name)

conda_install:
	$(CONDA_ACTIVATE) venv
	conda install $(name)

test:
	$(CONDA_ACTIVATE) venv
	python pytest

run_app:
	$(CONDA_ACTIVATE) venv
	python src/app.py

run_python: 
	$(CONDA_ACTIVATE) venv
	python $(script)

docs_view:
	@echo View API documentation... 
	pdoc src --http localhost:8080

docs_save:
	@echo Save documentation to docs... 
	pdoc src -o docs

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache

#include Makefile.venv