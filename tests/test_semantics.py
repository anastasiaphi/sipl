from sipl.parser import parse
from sipl.semantics import sem_P


def term(text):
    """Розбирає програму і будує її семантичний терм."""
    return sem_P(parse(text))

def test_power_from_practicum():
    program = """
    begin
      R := 1;
      while Y > 0 do
      begin
        R := R * X;
        Y := Y - 1
      end
    end
    """
    expected = "AS^R(1̄) • WH(S²(gr, Y⇒, 0̄), AS^R(S²(mult, R⇒, X⇒)) • AS^Y(S²(sub, Y⇒, 1̄)))"
    assert term(program) == expected

def test_assign():
    program = "begin x := 1 end"
    expected = "AS^x(1̄)"
    assert term(program) == expected


def test_variable_and_add():
    program = "begin x := x + 1 end"
    expected = "AS^x(S²(add, x⇒, 1̄))"
    assert term(program) == expected


def test_seq():
    program = "begin x := 1; y := 2 end"
    expected = "AS^x(1̄) • AS^y(2̄)"
    assert term(program) == expected


def test_skip():
    program = "begin skip end"
    expected = "id"
    assert term(program) == expected


def test_block():
    program = "begin begin x := 1 end end"
    expected = "AS^x(1̄)"
    assert term(program) == expected


def test_if():
    program = "begin if x > 0 then skip else x := 0 end"
    expected = "IF(S²(gr, x⇒, 0̄), id, AS^x(0̄))"
    assert term(program) == expected


def test_or():
    program = "begin if x > 1 ∨ x = 1 then skip else skip end"
    expected = "IF(S²(or, S²(gr, x⇒, 1̄), S²(eq, x⇒, 1̄)), id, id)"
    assert term(program) == expected

def test_not():
    program = "begin if ¬ x = 1 then skip else skip end"
    expected = "IF(S¹(neg, S²(eq, x⇒, 1̄)), id, id)"
    assert term(program) == expected
    
def test_priority_in_term():
    program = "begin x := 1 + 2 * 3 end"
    expected = "AS^x(S²(add, 1̄, S²(mult, 2̄, 3̄)))"
    assert term(program) == expected