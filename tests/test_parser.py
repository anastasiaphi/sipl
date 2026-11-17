from pathlib import Path

from sipl.parser import parse, parse_file, SiplSyntaxError
from sipl.ast import (
    Program, Assign, Seq, If, While, Block, Skip,
    Num, Var, BinOp, Compare, Or, Not,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

def test_assign():
    program = parse("begin x := 1 end")
    assert isinstance(program, Program)
    node = program.body
    assert isinstance(node, Assign)
    assert node.name == "x"
    assert isinstance(node.expr, Num)
    assert node.expr.value == 1


def test_negative_number():
    node = parse("begin x := -5 end").body
    assert node.expr.value == -5


def test_seq():
    node = parse("begin x := 1; y := 2 end").body
    assert isinstance(node, Seq)
    assert node.first.name == "x"
    assert node.second.name == "y"


def test_if():
    node = parse("begin if x > 0 then y := 1 else skip end").body
    assert isinstance(node, If)
    assert isinstance(node.cond, Compare)
    assert isinstance(node.then_branch, Assign)
    assert isinstance(node.else_branch, Skip)


def test_while_and_block():
    node = parse("begin while x > 0 do begin x := x - 1 end end").body
    assert isinstance(node, While)
    assert isinstance(node.body, Block)
    assert isinstance(node.body.body, Assign)


def test_arithmetic():
    expr = parse("begin x := 1 + 2 * 3 end").body.expr
    assert isinstance(expr, BinOp)
    assert expr.op == "+"
    assert isinstance(expr.left, Num)
    assert expr.right.op == "*"


def test_variable_in_expression():
    expr = parse("begin x := y - 1 end").body.expr
    assert expr.op == "-"
    assert isinstance(expr.left, Var)
    assert expr.left.name == "y"


def test_conditions():
    cond = parse("begin if ¬ x = 1 ∨ y > 2 then skip else skip end").body.cond
    assert isinstance(cond, Or)
    assert isinstance(cond.left, Not)
    assert cond.left.cond.op == "="
    assert cond.right.op == ">"


def test_examples():
    for file in EXAMPLES_DIR.glob("*.sipl"):
        program = parse_file(file)
        assert isinstance(program, Program)



def test_span():
    text = "begin\n  x := 1\nend"
    node = parse(text).body
    assert node.span.line == 2
    assert node.span.column == 3


def get_error(text):
    """Пробує розібрати текст і повертає помилку """
    try:
        parse(text)
    except SiplSyntaxError as error:
        return error
    return None


def test_error_position():
    error = get_error("begin x = 1 end")
    assert error is not None
    assert error.line == 1
    assert error.column == 9
    assert "':='" in error.message


def test_error_on_other_line():
    error = get_error("begin\n  while x > 0\n  x := 1\nend")
    assert error is not None
    assert error.line == 3
    assert error.column == 3


def test_error_unknown_symbol():
    error = get_error("begin x := 1 # end")
    assert error is not None
    assert "#" in error.message


def test_error_missing_end():
    error = get_error("begin x := 1")
    assert error is not None
    assert "закінчилась" in error.message