from pathlib import Path

from lark import Lark
from lark.exceptions import LarkError

PROJECT_DIR = Path(__file__).parent.parent
GRAMMAR_FILE = PROJECT_DIR / "src" / "sipl" / "sipl.lark"
EXAMPLES_DIR = PROJECT_DIR / "examples"

parser = Lark.open(str(GRAMMAR_FILE), start="program", parser="lalr")
GOOD_PROGRAMS = [
    "begin skip end",
    "begin x := 1 end",
    "begin x := 1; y := 2; z := 3 end",
    "begin x := (x + 1) * 2 end",
    "begin x := -5; y := x - -1 end",
    "begin if x > 0 then x := 1 else x := 2 end",
    "begin while x > 0 do x := x - 1 end",
    "begin while x > 0 do begin x := x - 1; y := y + 1 end end",
    "begin while ¬ M = N do if M > N then M := M - N else N := N - M end",
    "begin if x > 1 ∨ x = 1 then skip else skip end",
    "begin if not x = 1 or (y > 2) then skip else skip end",
    "begin if (x + 1) > 2 then skip else skip end",
    "begin begin x := 1 end end",
    "begin beginning := 1; ends := 2 end",
]

BAD_PROGRAMS = [
    "",                                            # порожня програма
    "x := 1",                                      # немає begin ... end
    "begin x := 1",                                # немає end
    "begin x = 1 end",                             # = замість :=
    "begin x := 1; end",                           # ; перед end
    "begin x := 1 y := 2 end",                     # немає ; між операторами
    "begin if x > 0 then x := 1 end",              # if без else
    "begin while x > 0 x := 1 end",                # while без do
    "begin x := 1 + end",                          # незакінчений вираз
    "begin x := (1 + 2 end",                       # незакрита дужка
    "begin 1 := x end",                            # зліва від := число
    "begin x := y > 1 end",                        # умова замість виразу
    "begin if x then skip else skip end",          # вираз замість умови
    "begin if x < 0 then skip else skip end",      # < немає в SIPL
    "begin while x > 0 do x := x - 1; y := 1 end end", # зайвий end 
]


def test_good_programs():
    for program in GOOD_PROGRAMS:
        parser.parse(program)


def test_bad_programs():
    for program in BAD_PROGRAMS:
        error = False
        try:
            parser.parse(program)
        except LarkError:
            error = True
        assert error, "Програма мала дати помилку: " + program


def test_examples():
    files = list(EXAMPLES_DIR.glob("*.sipl"))
    assert len(files) >= 3
    for file in files:
        text = file.read_text(encoding="utf-8")
        parser.parse(text)


def test_while_and_semicolon():
    tree = parser.parse("begin while x > 0 do x := x - 1; y := 1 end")
    seq = tree.children[0]
    assert seq.data == "seq"
    assert seq.children[0].data == "while_stmt"
    assert seq.children[1].data == "assign"


def test_mult_before_add():
    tree = parser.parse("begin x := 1 + 2 * 3 end")
    expr = tree.children[0].children[1]
    assert expr.data == "add"
    assert expr.children[1].data == "mult"


def test_minus_left_to_right():
    tree = parser.parse("begin x := 1 - 2 - 3 end")
    expr = tree.children[0].children[1]
    assert expr.data == "sub"
    assert expr.children[0].data == "sub"