from pathlib import Path

from sipl.cli import main

POWER_FILE = str(Path(__file__).parent.parent / "examples" / "power.sipl")


def test_check(capsys):
    code = main(["check", POWER_FILE])
    output = capsys.readouterr().out
    assert code == 0
    assert "OK" in output


def test_run(capsys):
    code = main(["run", POWER_FILE, "X=2", "Y=3"])
    output = capsys.readouterr().out
    assert code == 0
    assert "R ↦ 8" in output


def test_term(capsys):
    code = main(["term", POWER_FILE])
    output = capsys.readouterr().out
    assert code == 0
    assert "AS^R(1̄) • WH(" in output


def test_eval(capsys):
    code = main(["eval", POWER_FILE, "X=2", "Y=3"])
    output = capsys.readouterr().out
    assert code == 0
    assert "st3 = [X ↦ 2, Y ↦ 0, R ↦ 8]" in output


def test_parse(capsys):
    code = main(["parse", POWER_FILE])
    output = capsys.readouterr().out
    assert code == 0
    assert "While" in output


def test_file_not_found(capsys):
    code = main(["check", "no_such_file.sipl"])
    error = capsys.readouterr().err
    assert code == 1
    assert "не знайдено" in error


def test_syntax_error(tmp_path, capsys):
    bad_file = tmp_path / "bad.sipl"
    bad_file.write_text("begin x = 1 end", encoding="utf-8")
    code = main(["check", str(bad_file)])
    error = capsys.readouterr().err
    assert code == 1
    assert "Синтаксична помилка" in error


def test_missing_value(capsys):
    code = main(["run", POWER_FILE, "X=2"])
    error = capsys.readouterr().err
    assert code == 1
    assert "Y" in error


def test_wrong_value(capsys):
    code = main(["run", POWER_FILE, "X2"])
    error = capsys.readouterr().err
    assert code == 1
    assert "X=2" in error


def test_unknown_command(capsys):
    code = main(["hello", POWER_FILE])
    output = capsys.readouterr().out
    assert code == 1
    assert "Використання" in output