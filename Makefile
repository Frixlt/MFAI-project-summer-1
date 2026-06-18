.PHONY: install lint format pre-commit-install pre-commit-run clean test cov-badge help
.DEFAULT_GOAL := help

install: ## Установить все зависимости проекта
	uv sync --all-extras

lint: ## Запустить проверку стиля кода линтером Ruff
	uv run ruff check .

format: ## Форматировать код с помощью Ruff
	uv run ruff format .

pre-commit-install: ## Установить хуки pre-commit
	uv run pre-commit install

pre-commit-run: ## Запустить все хуки pre-commit для файлов
	uv run pre-commit run --all-files

test: ## Запустить тесты с расчетом покрытия кода
	uv run pytest

cov-badge: ## Сгенерировать бейдж покрытия кода (Coverage Badge)
	uv run python3 .github/scripts/generate_badge.py -o .github/badges/coverage.svg -f

clean: ## Очистить кэш-файлы и временные директории
	rm -rf .venv/
	rm -rf .ruff_cache/
	rm -rf .pytest_cache/
	rm -rf .ipynb_checkpoints/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -r {} +

help: ## Показать это справочное сообщение
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
