.PHONY: install lint format pre-commit-install pre-commit-run clean help
.DEFAULT_GOAL := help

install:
	uv sync --all-extras

lint:
	uv run ruff check .

format:
	uv run ruff format .

pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files

clean:
	rm -rf .venv/
	rm -rf .ruff_cache/
	rm -rf .pytest_cache/
	rm -rf .ipynb_checkpoints/
	find . -type d -name "__pycache__" -exec rm -r {} +

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
