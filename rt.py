import argparse
import ast
import copy
import random
import string

import astor

target_args = []
branch_lineno = [0]
guesses = {}


def not_supported(ast):
    print('Not Supported: %s' % type(ast).__name__)
    exit(1)


def save_guess(lineno, tf, vari):
    global guesses
    guessing = '%d%s' % (branch_lineno.index(lineno), 'T' if tf else 'F')
    guessed_args = []
    for arg in target_args:
        if type(vari[arg]) == ast.Num:
            guessed_args.append(str(eval(astor.to_source(vari[arg]))))
        elif type(vari[arg]) == ast.Name:
            guessed_args.append('0')
        else:
            raise Exception('Unknown Error')
    guesses[guessing] = ', '.join(guessed_args)


def find_vari(expr):
    if type(expr) == ast.Name:
        return {expr.id}
    elif type(expr) == ast.Num:
        return set()
    elif type(expr) == ast.Str:
        return set()
    elif type(expr) == ast.BinOp:
        return find_vari(expr.left) | find_vari(expr.right)
    elif type(expr) == ast.Call:
        varis = set()
        for arg in expr.args:
            varis |= find_vari(arg)
        return varis
    else:
        not_supported(expr)


def sub_vari(expr, vari):
    if type(expr) == ast.Name:
        if expr.id in vari:
            return vari[expr.id]
        else:
            print('Variable Not Defined: %s' % expr.id)
            exit(1)
    elif type(expr) == ast.Num:
        return expr
    elif type(expr) == ast.Str:
        return expr
    elif type(expr) == ast.BinOp:
        expr.left = sub_vari(expr.left, vari)
        expr.right = sub_vari(expr.right, vari)
        return expr
    elif type(expr) == ast.Call:
        for i, arg in enumerate(expr.args):
            expr.args[i] = sub_vari(arg, vari)
        return expr
    else:
        not_supported(expr)


def b_dist(ops, left, right):
    if type(ops) == ast.Eq:
        return eval('1 - 1.001**-abs(%s - %s)' % (left, right))
    elif type(ops) == ast.NotEq:
        return eval('1 - 1.001**abs(%s - %s)' % (left, right))
    elif type(ops) == ast.Lt:
        return eval('1 - 1.001**(%s - %s)' % (right, left))
    elif type(ops) == ast.Gt:
        return eval('1 - 1.001**(%s - %s)' % (left, right))
    elif type(ops) == ast.LtE:
        return eval('1 - 1.001**(%s - %s)' % (right, left))
    elif type(ops) == ast.GtE:
        return eval('1 - 1.001**(%s - %s)' % (left, right))
    else:
        print('%s Not Supported' % type(ops).__name__)
        exit(1)


def is_satisfied(ops, f):
    if type(ops) == ast.Eq:
        return f == 0
    elif type(ops) == ast.NotEq:
        return f < 0
    elif type(ops) == ast.Lt:
        return f < 0
    elif type(ops) == ast.Gt:
        return f < 0
    elif type(ops) == ast.LtE:
        return f <= 0
    elif type(ops) == ast.GtE:
        return f <= 0
    else:
        print('%s Not Supported' % type(ops).__name__)
        exit(1)


def neg(pred):
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


def rt(pred):
    left = pred.left
    ops = pred.ops[0]
    right = pred.comparators[0]

    vari = find_vari(left) | find_vari(right)

    length = 0
    guess_depth1 = 0

    count = 0
    while True:
        length += 1
        guess_depth1 += 1
        guess_depth2 = 0
        if guess_depth1 > 3:  # max length
            break
        while True:
            count += 1
            print(count)
            guess = {x: ast.Str(gen_rand_str(length)) for x in vari}
            print(guess["a"].s)
            guess_depth2 += 1
            if not vari:
                return guess
            if guess_depth2 > 100000:
                break
            if is_satisfied2(guess, ops, left, right):
                return guess


def gen_rand_str(length):
    s = ""
    alpha = "qwertyuiopasdfghjklzxcvbnm"
    for i in range(length):
        s += random.choice(alpha)
    return s


def is_satisfied2(guess, ops, left, right):
    if type(ops) == ast.Eq and type(left)==ast.Name:
        # print(guess, left.id, guess[left.id].s, right.s)
        return guess[left.id].s == right.s
    else:
        print("is_satisfied2: yet ")


def c_branch(stmt):
    global branch_lineno
    if type(stmt) == list:
        for e in stmt:
            c_branch(e)
    elif type(stmt) == ast.If or type(stmt) == ast.While:
        branch_lineno.append(stmt.lineno)
        c_branch(stmt.body)
        c_branch(stmt.orelse)


def e_stmt(stmt, vari):
    vari = copy.deepcopy(vari)
    if type(stmt) == list:
        for e in stmt:
            if type(e) == ast.Return:
                break
            vari = e_stmt(e, vari)
    elif type(stmt) == ast.If or type(stmt) == ast.While:
        lineno = stmt.lineno
        if len(stmt.test.comparators) != 1 or len(stmt.test.ops) != 1:
            print('%d: ' % lineno, end='')
            not_supported(stmt.test)
        stmt.test.left = e_expr(stmt.test.left, vari)
        stmt.test.comparators[0] = e_expr(stmt.test.comparators[0], vari)
        if type(stmt.test.left) == ast.Num and type(
                stmt.test.comparators[0]) == ast.Num:
            fin = eval(astor.to_source(stmt.test))
            if fin:
                save_guess(lineno, True, vari)
                e_stmt(stmt.body, vari)
            else:
                save_guess(lineno, False, vari)
                e_stmt(stmt.orelse, vari)
        else:
            guess_true = rt(stmt.test)
            guess_false = rt(neg(stmt.test))
            vari_true = vari_false = None
            if guess_true:
                vari_true = vari
                vari_true.update(guess_true)
                save_guess(lineno, True, vari_true)
            if guess_false:
                vari_false = copy.deepcopy(vari)
                vari_false.update(guess_false)
                save_guess(lineno, False, vari_false)
            if vari_true:
                e_stmt(stmt.body, vari_true)
            if vari_false:
                e_stmt(stmt.orelse, vari_false)
    elif type(stmt) == ast.Expr:
        e_expr(stmt.value, vari)
    elif type(stmt) == ast.Assign:
        for target in stmt.targets:
            if type(target) == ast.Name:
                vari[target.id] = e_expr(stmt.value, vari)
            else:
                print('Cannot assign to %s: %s' %
                      (type(target).__name__, astor.to_source(target).strip()))
                exit(1)
    elif type(stmt) == ast.AugAssign:
        if type(stmt.target) == ast.Name:
            expr = ast.BinOp()
            expr.left = stmt.target
            expr.op = stmt.op
            expr.right = e_expr(stmt.value, vari)
            vari[stmt.target.id] = e_expr(expr, vari)
        else:
            print('Cannot assign to %s: %s' % (type(
                stmt.target).__name__, astor.to_source(stmt.target).strip()))
            exit(1)
    elif type(stmt) == ast.Pass:
        pass
    else:
        not_supported(stmt)
    return vari


def e_expr(expr, vari):
    if type(expr) == ast.Name:
        if expr.id in vari:
            return vari[expr.id]
        else:
            print('Variable Not Defined: %s' % expr.id)
            exit(1)
    elif type(expr) == ast.Call:
        args = []
        all_int = True
        for arg in expr.args:
            arg = e_expr(arg, vari)
            args.append(arg)
            if type(arg) != ast.Num:
                all_int = False
        expr.args = args
        if all_int:
            try:
                res = eval(astor.to_source(expr))
            except NameError:
                print('Function Not Defined: %s' % expr.func.id)
                exit(1)
            return ast.Num(res)
        else:
            return expr
        return expr
    elif type(expr) == ast.Num:
        return expr
    elif type(expr) == ast.BinOp:
        expr.left = e_expr(expr.left, vari)
        expr.right = e_expr(expr.right, vari)
        if type(expr.left) == ast.Num and type(expr.right) == ast.Num:
            return ast.Num(eval(astor.to_source(expr)))
        return expr
    else:
        not_supported(expr)


def test_pred(pred: str):
    print( rt(ast.parse(pred).body[0].value)['a'].s )


if __name__ == '__main__':
    # test_pred("a=='b'")
    test_pred("a=='abb'")
    # print(ast.dump(ast.parse("a=='ab'")))
    # parser = argparse.ArgumentParser()
    # parser.add_argument('input', type=str)
    # args = parser.parse_args()
    #
    # tree = astor.parse_file(args.input)
    #
    # target_fn = None
    # for node in tree.body:
    #     if type(node) == ast.Import:
    #         exec(astor.to_source(node))
    #     elif type(node) == ast.FunctionDef:
    #         exec(astor.to_source(node))
    #         target_fn = node
    #
    # target_args = list(map(lambda x: x.arg, target_fn.args.args))
    # vari = {x: ast.Name(x) for x in target_args}
    # c_branch(target_fn.body)
    # branch_lineno = sorted(branch_lineno)
    # e_stmt(target_fn.body, vari)
    #
    # for line in range(1, len(branch_lineno)):
    #     for tf in ['T', 'F']:
    #         key = '%d%s' % (line, tf)
    #         print(key, end=': ')
    #         try:
    #             print(guesses[key])
    #         except KeyError:
    #             print('-')
