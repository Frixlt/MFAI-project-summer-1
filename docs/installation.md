# Инструкция по установке и настройке проекта

Для работы с проектом используется менеджер пакетов [uv](https://github.com/astral-sh/uv). Он обеспечивает быструю установку зависимостей и изоляцию виртуального окружения.

---

## 1. Установка uv

### Windows

Запустите PowerShell от имени пользователя и выполните:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### macOS / Linux

Выполните команду в терминале:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 2. Клонирование репозитория

Склонируйте проект и перейдите в его рабочую директорию:

```bash
git clone https://github.com/Frixlt/MFAI-project-summer-1.git
cd MFAI-project-summer-1
```

---

## 3. Настройка окружения и зависимостей

Установите виртуальное окружение `.venv` и зависимости (включая инструменты линтинга):

```bash
make install
```

_Или напрямую через uv:_

```bash
uv sync --all-extras
```

---

## 4. Настройка pre-commit хуков

Для автоматического форматирования и проверки стиля кода при каждом коммите установите pre-commit хуки в git:

```bash
make pre-commit-install
```

_Или напрямую через uv:_

```bash
uv run pre-commit install
```

---

## Доступные команды разработки (Makefile)

В корне проекта находится `Makefile`, предоставляющий ярлыки для рутинных задач:

- `make install` — создать виртуальное окружение и установить зависимости.
- `make lint` — проверить код линтером Ruff.
- `make format` — автоматически исправить ошибки стиля и отформатировать код.
- `make pre-commit-run` — принудительно запустить pre-commit хуки на всех файлах.
- `make clean` — очистить временные файлы, кэш Ruff/pytest и Jupyter checkpoints.
