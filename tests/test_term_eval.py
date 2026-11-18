from sipl.parser import parse
from sipl.term_eval import explain
from sipl.interpreter import SiplRuntimeError


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


def test_power_result():
    state, lines = explain(parse(POWER), {"X": 2, "Y": 3})
    assert state == {"X": 2, "Y": 0, "R": 8}


def test_power_states():
    state, lines = explain(parse(POWER), {"X": 2, "Y": 3})
    assert "st0 = [X ↦ 2, Y ↦ 3, R ↦ 1]" in lines
    assert "st1 = [X ↦ 2, Y ↦ 2, R ↦ 2]" in lines
    assert "st2 = [X ↦ 2, Y ↦ 1, R ↦ 4]" in lines
    assert "st3 = [X ↦ 2, Y ↦ 0, R ↦ 8]" in lines


def test_power_conditions():
    state, lines = explain(parse(POWER), {"X": 2, "Y": 3})
    text = "\n".join(lines)
    assert "gr(3, 0) = true" in text
    assert "gr(0, 0) = false" in text
    assert "вихід з циклу" in text


def test_assign_explanation():
    state, lines = explain(parse("begin x := x * 2 + 1 end"), {"x": 5})
    text = "\n".join(lines)
    assert "x ↦ add(mult(5, 2), 1) = 11" in text
    assert "AF_AS" in text


def test_if_explanation():
    state, lines = explain(parse("begin if x > 0 then y := 1 else y := 2 end"), {"x": -3})
    text = "\n".join(lines)
    assert "gr(-3, 0) = false" in text
    assert "гілку else" in text
    assert state["y"] == 2


def test_not_and_skip():
    state, lines = explain(parse("begin if ¬ x = 1 then skip else skip end"), {"x": 1})
    text = "\n".join(lines)
    assert "neg(eq(1, 1)) = false" in text
    assert "AF_ID" in text


def test_term_in_explanation():
    state, lines = explain(parse("begin x := 1 end"), {})
    assert lines[0] == "Терм: AS^x(1̄)"


def test_infinite_loop():
    error = None
    try:
        explain(parse("begin while 1 > 0 do skip end"), {}, max_steps=50)
    except SiplRuntimeError as e:
        error = e
    assert error is not None



