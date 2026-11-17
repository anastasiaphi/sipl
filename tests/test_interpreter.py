from sipl.parser import parse
from sipl.interpreter import run_program, format_state, SiplRuntimeError


def run(text, state):
    """Розбирає програму і виконує її на стані state"""
    program = parse(text)
    return run_program(program, state)


def get_error(text, state, max_steps=10000):
    """Виконує програму і повертає помилку виконання """
    try:
        run_program(parse(text), state, max_steps)
    except SiplRuntimeError as error:
        return error
    return None


POWER = """
begin
  R := 1;
  while Y > 0 do
  begin
    R := R * X;
    Y := Y - 1
  end
end
"""

GCD = """
begin
  while ¬ M = N do
    if M > N then M := M - N else N := N - M
end
"""

DIV = """
begin
  R := 0;
  while X > Y ∨ X = Y do
  begin
    X := X - Y;
    R := R + 1
  end
end
"""


def test_power():
    # 2^3 = 8, як у задачі В1
    result = run(POWER, {"X": 2, "Y": 3})
    assert result == {"X": 2, "Y": 0, "R": 8}


def test_power_from_practicum():
    result = run(POWER, {"X": 5, "Y": 2})
    assert result["R"] == 25


def test_power_zero():
    result = run(POWER, {"X": 7, "Y": 0})
    assert result["R"] == 1


def test_gcd():
    result = run(GCD, {"M": 8, "N": 16})
    assert result["M"] == 8
    assert result["N"] == 8


def test_div():
    result = run(DIV, {"X": 7, "Y": 4})
    assert result["R"] == 1
    assert result["X"] == 3


def test_assign_and_seq():
    result = run("begin x := 1; y := x + 1; x := 10 end", {})
    assert result == {"x": 10, "y": 2}


def test_arithmetic():
    result = run("begin a := 1 + 2 * 3; b := (1 + 2) * 3; c := 1 - 2 - 3; d := -5 end", {})
    assert result == {"a": 7, "b": 9, "c": -4, "d": -5}


def test_if_then():
    result = run("begin if x > 0 then y := 1 else y := 2 end", {"x": 5})
    assert result["y"] == 1


def test_if_else():
    result = run("begin if x > 0 then y := 1 else y := 2 end", {"x": -5})
    assert result["y"] == 2


def test_conditions():
    program = "begin if ¬ x = 1 ∨ x > 10 then r := 1 else r := 0 end"
    assert run(program, {"x": 1})["r"] == 0    
    assert run(program, {"x": 5})["r"] == 1     
    assert run(program, {"x": 1})["x"] == 1


def test_skip_and_block():
    result = run("begin begin skip; x := 3 end end", {})
    assert result == {"x": 3}


def test_input_state_not_changed():
    start = {"X": 2, "Y": 3}
    run(POWER, start)
    assert start == {"X": 2, "Y": 3}



def test_undefined_variable():
    error = get_error("begin y := x + 1 end", {})
    assert error is not None
    assert "x" in error.message
    assert error.span.line == 1


def test_infinite_loop():
    error = get_error("begin while 1 > 0 do skip end", {}, max_steps=100)
    assert error is not None
    assert "ліміт" in error.message


def test_format_state():
    assert format_state({"X": 2, "Y": 0, "R": 8}) == "[X ↦ 2, Y ↦ 0, R ↦ 8]"