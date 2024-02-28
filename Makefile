SHELL := /bin/bash
PROJECT_PATH := $(shell git rev-parse --show-toplevel)
VENVNAME := .venv
VENVPATH := $(HOME)/miniconda3/envs/housing/bin
PYTHON_VERSION := "3.9"
export PYTHONPATH := libs:apps
CPUS_FOR_TEST := 2

determine_python = \
        det_python=; \
        for opt in python"$(PYTHON_VERSION)" python3 python; do \
          if type "$${opt}" &>/dev/null ; then det_python=$$opt; break; fi; \
        done; \
        if [ -z "$$det_python" ]; then echo 1>&2 "Unable to find python "; exit 2; else $$det_python -V ; fi

SRC_DIR := api/
TEST_DIR := tests/

LINT_MAX_LINE_LENGTH := 110

format:
	#yapf ${SRC_DIR} ${TEST_DIR} -r -i
	@echo "== isort ==" && $(VENVPATH)/isort --profile black -l $(LINT_MAX_LINE_LENGTH) $(SRC_DIR) $(TEST_DIR)
	@echo "== Black ==" && $(VENVPATH)/black -C --line-length $(LINT_MAX_LINE_LENGTH) --target-version py38 $(SRC_DIR) $(TEST_DIR) *.py

lint: format
	@echo "== PyLint ==" && $(VENVPATH)/pylint $(SRC_DIR) $(TEST_DIR) || true
	@echo ""
	@echo "== Flake8 ==" && $(VENVPATH)/flake8 --max-line-length=$(LINT_MAX_LINE_LENGTH) $(SRC_DIR) || true
	@echo ""
	@echo "== mypy ==" && $(VENVPATH)/mypy --python-version 3.9 --ignore-missing-imports $(SRC_DIR) $(TEST_DIR) || true
	@echo ""

test:
	$(VENVPATH)/pytest -n $(CPUS_FOR_TEST) $(TEST_DIR) --capture=no --tb=line -v
	#$(VENVPATH)/pytest -n $(CPUS_FOR_TEST) $(TEST_DIR) --cov $(SRC_DIR) --capture=no

clean:
	@rm -vrf build
	@rm -vrf dist
	@rm -vrf deps
	@rm -vrf src.egg-info
	@rm -vrf .mypy_cache |grep "directory" || true
	@rm -vrf .pytest_cache
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
	@find . | grep -E "(\.log$$)" | xargs rm -rf
	@rm -vrf mle_project_challenge.egg-info
