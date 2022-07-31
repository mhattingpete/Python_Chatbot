.PHONY: notebook docs
.EXPORT_ALL_VARIABLES:

install: 
	@echo "Installing..."
	python3 -m venv venv
	$(VENV)/pip install -r requirements.txt
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
	$(VENV)/pip freeze > requirements.txt

test:
	$(VENV)/pytest

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

include Makefile.venv