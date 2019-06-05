import ast
import copy
import random
import string
import unittest
from typing import Dict, List

import astor

import calcfitness
import minLength

branch_lineno = [0]


def b_dist(pred: ast.Compare) -> float:
    left = pred.left
    right = pred.comparators[0]
    assert (type(left) == ast.Str)
    assert (type(right) == ast.Str)
    assert (len(left.s) == len(right.s))

    dist = 0
    for i in range(len(left.s)):
        dist += abs(ord(left.s[i]) - ord(right.s[i]))
    return dist


def make_rand_str_length(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def sub_expr(expr: ast.Expr, env: List[Dict[str, str]]) -> ast.Expr:
    if type(expr) == ast.Name:
        return ast.Str(env[expr.id])
    elif type(expr) == ast.Compare:
        expr = copy.deepcopy(expr)
        expr.left = sub_expr(expr.left, env)
        expr.comparators = [sub_expr(x, env) for x in expr.comparators]
        return expr
    elif type(expr) == ast.Str:
        return expr
    elif type(expr) == ast.Subscript:
        if type(expr.value) == ast.Name:
            if type(expr.slice) == ast.Index:
                return ast.Str(env[expr.value.id][expr.slice.value.n])
            elif type(expr.slice) == ast.Slice:
                return ast.Str(
                    env[expr.value.id][expr.slice.lower.n:expr.slice.upper.n])
    raise Exception(ast.dump(expr))


def manip_str(src: str, idx: int, off: int) -> str:
    # mini = 0
    # maxi = 0x110000 - 1
    mini = ord('A')
    maxi = ord('z')
    res = max(mini, min(ord(src[idx]) + off, maxi))
    return src[:idx] + chr(res) + src[idx + 1:]


def is_satisfied(preds: List[ast.Compare], env):
    sat = True
    for pred in preds:
        sat = eval(astor.to_source(sub_expr(pred, env)))
        if not sat:
            break
    return sat


def add_all_dist(preds: List[ast.Compare], env):
    dist = 0
    for pred in preds:
        dist += calcfitness.calc_b_dist(sub_expr(pred, env))
    return dist


def avm(preds: List[ast.Compare]) -> Dict[str, str]:
    # assert (len(pred.ops) == 1)
    # assert (len(pred.comparators) == 1)
    # assert (type(pred.ops[0]) == ast.Eq)

    global minlen
    guess = {}
    for pred in preds:
        for a in ast.walk(pred):
            if type(a) == ast.Name:
                guess[a.id] = make_rand_str_length(4)

    if is_satisfied(preds, guess):
        return guess
    elif not guess:
        return None

    while True:
        for vari in guess:
            for ptr in range(len(guess[vari])):
                # exploratory move
                str_dec = manip_str(guess[vari], ptr, -1)
                str_inc = manip_str(guess[vari], ptr, +1)
                guess_dec = copy.deepcopy(guess)
                guess_inc = copy.deepcopy(guess)
                guess_dec[vari] = str_dec
                guess_inc[vari] = str_inc
                f_dec = add_all_dist(preds, guess_dec)
                f_inc = add_all_dist(preds, guess_inc)
                direction = 1 if f_inc < f_dec else -1
                amp = 1
                prev_f = add_all_dist(preds, guess)

                # pattern move
                while True:
                    new_guess = copy.deepcopy(guess)
                    new_guess[vari] = manip_str(guess[vari], ptr,
                                                direction * amp)
                    f = add_all_dist(preds, new_guess)
                    if is_satisfied(preds, new_guess):
                        return new_guess
                    elif f < prev_f:
                        amp *= 2
                        prev_f = f
                        guess = new_guess
                    else:
                        break

    return guess


def test_pred(pred: str):
    return avm(ast.parse(pred).body[0].value)


class TestAVM(unittest.TestCase):
    def test_always_true(self):
        self.assertEqual(test_pred("'a' == 'a'"), {})

    def test_always_false(self):
        self.assertEqual(test_pred("'a' == 'b'"), None)

    def test_fit(self):
        rand = make_rand_str_length(random.randint(0, 10))
        self.assertEqual(test_pred("a == '%s'" % rand), {'a': rand})
        self.assertEqual(test_pred("'%s' == a" % rand), {'a': rand})

    def test_part(self):
        res = test_pred("a[3] == 'a'")
        self.assertEqual(res['a'][3], 'a')

    # def test_slice(self):
    #     res = test_pred("a[1:3] == 'ab'")
    #     self.assertEqual(res['a'][1:3], 'ab')

    def test_same(self):
        res = test_pred("a == b")
        self.assertEqual(res['a'], res['b'])

    def test_same_part(self):
        res = test_pred("a[3] == b[3]")
        self.assertEqual(res['a'][3], res['b'][3])


def neg(pred):
    pred = copy.deepcopy(pred)
    ops = pred.ops[0]
    if type(ops) == ast.Eq:
        pred.ops[0] = ast.NotEq()
        return pred
    elif type(ops) == ast.NotEq:
        pred.ops[0] = ast.Eq()
        return pred
    elif type(ops) == ast.Lt:
        pred.ops[0] = ast.GtE()
        return pred
    elif type(ops) == ast.Gt:
        pred.ops[0] = ast.LtE()
        return pred
    elif type(ops) == ast.LtE:
        pred.ops[0] = ast.Gt()
        return pred
    elif type(ops) == ast.GtE:
        pred.ops[0] = ast.Lt()
        return pred
    else:
        print('%s Not Supported' % type(ops).__name__)
        exit(1)


def c_branch(stmt):
    global branch_lineno
    if type(stmt) == list:
        for e in stmt:
            c_branch(e)
    elif type(stmt) == ast.If or type(stmt) == ast.While:
        branch_lineno.append(stmt.lineno)
        c_branch(stmt.body)
        c_branch(stmt.orelse)


cond_tree = {}


def extract_condition(stmt: ast.stmt, conds: List[ast.Compare] = []):
    conds = copy.deepcopy(conds)
    if type(stmt) == list:
        for smt in stmt:
            extract_condition(smt, conds)
    elif type(stmt) == ast.If:
        cond_true = copy.deepcopy(conds)
        cond_false = copy.deepcopy(conds)
        cond_true.append(stmt.test)
        cond_false.append(neg(stmt.test))
        cond_tree[branch_lineno.index(stmt.lineno)] = {
            'T': cond_true,
            'F': cond_false
        }
        extract_condition(stmt.body, cond_true)
        extract_condition(stmt.orelse, cond_false)
    elif type(stmt) == ast.Pass:
        pass
    else:
        raise Exception(ast.dump(stmt))


if __name__ == '__main__':
    tree = astor.parse_file('target.py')

    target_fn = None
    for node in tree.body:
        if type(node) == ast.Import:
            exec(astor.to_source(node))
        elif type(node) == ast.FunctionDef:
            exec(astor.to_source(node))
            target_fn = node

    c_branch(target_fn.body)
    branch_lineno = sorted(branch_lineno)

    # global minlen
    # minlen = minLength.minLength(target_fn)

    extract_condition(target_fn.body)
    for i in cond_tree:
        for tf in cond_tree[i]:
            print(
                "%d%s:" % (i, tf), " and ".join(
                    [astor.to_source(x).strip() for x in cond_tree[i][tf]]))
            print(avm(cond_tree[i][tf]))
