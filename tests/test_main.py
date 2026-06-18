from src.main import main

__all__ = ()


def test_main() -> None:
    """Проверить запуск точки входа"""
    assert main() is None
