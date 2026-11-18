# sipl
![CI](https://github.com/anastasiaphi/sipl/actions/workflows/ci.yml/badge.svg)
Проєкт з теорії програмування.
Парсер, інтерпретатор і семантичні терми для мови SIPL.

Завдання: CORE-01, CORE-02, CORE-03, CORE-05, SEM-01, SEM-02, REL-01, REL-02 (10 балів).

## Як встановити

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Як запускати

```
sipl check examples/power.sipl          перевірка синтаксису
sipl parse examples/power.sipl          дерево програми
sipl run examples/power.sipl X=2 Y=3    виконання
sipl term examples/power.sipl           семантичний терм
sipl eval examples/power.sipl X=2 Y=3   обчислення терму з поясненням
```

Початкові значення змінних пишуться після файлу (X=2 Y=3)

## Структура проекту

- `src/sipl/sipl.lark` - граматика
- `src/sipl/parser.py` - парсер (текст -> дерево)
- `src/sipl/interpreter.py` - виконання програми
- `src/sipl/semantics.py` - семантичний терм
- `src/sipl/term_eval.py` - обчислення терму на стані
- `src/sipl/cli.py` - команди sipl
- `examples/` - приклади програм
- `tests/` - тести
## Тести

```
pytest 
```
Запустити тести з одного файлу, наприклад тільки граматику:

```
pytest tests/test_grammar.py -v
```

Що перевіряють тести:

- `test_grammar.py` - граматика: правильні програми розбираються, неправильні дають помилку
- `test_parser.py` - парсер: правильне дерево, позиції в тексті, повідомлення про помилки
- `test_interpreter.py` - виконання програм, помилки виконання, зациклення
- `test_semantics.py` - побудова семантичного терму 
- `test_term_eval.py` - обчислення терму на стані, стани після кожної ітерації
- `test_cli.py` - команди sipl і їх повідомлення про помилки
