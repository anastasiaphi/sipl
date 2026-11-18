from sipl.ast import (
    Assign, Seq, If, While, Block, Skip,
    Num, Var, BinOp, Compare, Or, Not,
)

ARITHMETIC = {"+": "add", "-": "sub", "*": "mult"}
COMPARISON = {"=": "eq", ">": "gr"}


def constant(n):
    """Константна функція n̄ """
    return str(n) + "\u0304"


def sem_P(program):
    # NS_Prog: sem_P(begin S end) = sem_S(S)
    return sem_S(program.body)


def sem_S(node):
    """Терм для оператора"""
    if isinstance(node, Assign):
        # NS_Stm_As: sem_S(x := a) = AS^x(sem_A(a))
        return f"AS^{node.name}({sem_A(node.expr)})"

    elif isinstance(node, Seq):
        # NS_Stm_Seq: sem_S(S1 ; S2) = sem_S(S1) • sem_S(S2)
        return sem_S(node.first) + " • " + sem_S(node.second)

    elif isinstance(node, If):
        # NS_Stm_If: sem_S(if b then S1 else S2) = IF(sem_B(b), sem_S(S1), sem_S(S2))
        return f"IF({sem_B(node.cond)}, {sem_S(node.then_branch)}, {sem_S(node.else_branch)})"

    elif isinstance(node, While):
        # NS_Stm_Wh: sem_S(while b do S) = WH(sem_B(b), sem_S(S))
        return f"WH({sem_B(node.cond)}, {sem_S(node.body)})"

    elif isinstance(node, Block):
        # NS_Stm_BE: sem_S(begin S end) = sem_S(S)
        return sem_S(node.body)

    elif isinstance(node, Skip):
        # NS_Stm_Skip: sem_S(skip) = id
        return "id"


def sem_A(node):
    """Терм для арифметичного виразу."""
    if isinstance(node, Num):
        # NS_A_Num: sem_A(n) = n̄
        return constant(node.value)

    elif isinstance(node, Var):
        # NS_A_Var: sem_A(x) = x⇒
        return node.name + "⇒"

    elif isinstance(node, BinOp):
        # NS_A_Add / Sub / Mult: sem_A(a1 + a2) = S²(add, sem_A(a1), sem_A(a2))
        name = ARITHMETIC[node.op]
        return f"S²({name}, {sem_A(node.left)}, {sem_A(node.right)})"


def sem_B(node):
    """Терм для умови."""
    if isinstance(node, Compare):
        # NS_B_eq / NS_B_gr: sem_B(a1 > a2) = S²(gr, sem_A(a1), sem_A(a2))
        name = COMPARISON[node.op]
        return f"S²({name}, {sem_A(node.left)}, {sem_A(node.right)})"

    elif isinstance(node, Or):
        # NS_B_or: sem_B(b1 ∨ b2) = S²(or, sem_B(b1), sem_B(b2))
        return f"S²(or, {sem_B(node.left)}, {sem_B(node.right)})"

    elif isinstance(node, Not):
        # NS_B_neg: sem_B(¬b) = S¹(neg, sem_B(b))
        return f"S¹(neg, {sem_B(node.cond)})"