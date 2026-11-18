import sys

from sipl.parser import parse_file, SiplSyntaxError
from sipl.ast import show_tree
from sipl.interpreter import run_program, format_state, SiplRuntimeError
from sipl.semantics import sem_P
from sipl.term_eval import explain

HELP = """Використання: sipl <команда> <файл> [значення]

Команди:
  check  - перевірити синтаксис програми
  parse  - показати AST програми
  run    - виконати програму
  term   - побудувати семантичний терм
  eval   - обчислити терм на стані з поясненням

Приклад: sipl run examples/power.sipl X=2 Y=3"""

COMMANDS = ["check", "parse", "run", "term", "eval"]


def parse_values(items):
    """Перетворює ["X=2", "Y=3"] на словник {"X": 2, "Y": 3}."""
    state = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"неправильне значення '{item}', треба писати так: X=2")
        name, value = item.split("=", 1)
        if not value.lstrip("-").isdigit():
            raise ValueError(f"значення '{item}' має бути цілим числом")
        state[name] = int(value)
    return state


def main(args=None):
    """Запуск програми. Повертає код виходу: 0 - успіх, 1 - помилка."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if args is None:
        args = sys.argv[1:]

    if len(args) < 2 or args[0] not in COMMANDS:
        print(HELP)
        return 1

    command = args[0]       # наприклад "run"
    file = args[1]          # наприклад "examples/power.sipl"
    values = args[2:]       # наприклад ["X=2", "Y=3"]

    try:
        program = parse_file(file)

        if command == "check":
            print("OK: програма синтаксично правильна")

        elif command == "parse":
            print(show_tree(program, with_spans=True), end="")

        elif command == "run":
            state = parse_values(values)
            result = run_program(program, state)
            print(format_state(result))

        elif command == "term":
            print(sem_P(program))

        elif command == "eval":
            state = parse_values(values)
            result, lines = explain(program, state)
            for line in lines:
                print(line)

    except FileNotFoundError:
        print(f"Помилка: файл '{file}' не знайдено", file=sys.stderr)
        return 1
    except (SiplSyntaxError, SiplRuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())