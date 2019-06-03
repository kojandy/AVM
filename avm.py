import ast
import copy
import random
import string
import unittest
from typing import Dict, List

import astor
import calcfitness


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
    res = max(0, min(ord(src[idx]) + off, 0x110000 - 1))
    return src[:idx] + chr(res) + src[idx + 1:]


def avm(pred: ast.Compare) -> Dict[str, str]:
    assert (len(pred.ops) == 1)
    assert (len(pred.comparators) == 1)
    # assert (type(pred.ops[0]) == ast.Eq)

    length = 0
    if type(pred.left) == ast.Str:
        length = len(pred.left.s)
    elif type(pred.comparators[0]) == ast.Str:
        length = len(pred.comparators[0].s)

    while True:
        try:
            guess = {}
            for a in ast.walk(pred):
                if type(a) == ast.Name:
                    guess[a.id] = make_rand_str_length(length)

            if eval(astor.to_source(sub_expr(pred, guess))):
                return guess
            elif not guess:
                return None

            break
        except IndexError:
            length += 1

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
                f_dec = calcfitness.calc_b_dist(sub_expr(pred, guess_dec))
                f_inc = calcfitness.calc_b_dist(sub_expr(pred, guess_inc))
                direction = 1 if f_inc < f_dec else -1
                amp = 1
                prev_f = calcfitness.calc_b_dist(sub_expr(pred, guess))

                # pattern move
                while True:
                    new_guess = copy.deepcopy(guess)
                    new_guess[vari] = manip_str(guess[vari], ptr,
                                                direction * amp)
                    f = calcfitness.calc_b_dist(sub_expr(pred, new_guess))
                    if eval(astor.to_source(sub_expr(pred, new_guess))):
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


if __name__ == '__main__':
    unittest.main()
