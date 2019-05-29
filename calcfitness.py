import ast


def b_dist(op, left, right):
    if len(left)!=len(right):
        print('not same length: %s %s' % left, right)
        exit(1)

    d=0
    if type(op) == ast.Eq:
        for i in range(len(left)):
            d += eval('abs(%s - %s)' % (ord(left[i]), ord(right[i])))
        return d


def normalise(n):
    return eval('1 - 1.001**-n)' % n)


def test(actual, expected):
    import sys
    linenum = sys._getframe(1).f_lineno  # get the caller's line number.
    if (expected == actual):
        msg = "Line:{0}  PASS".format(linenum)
    else:
        msg = ("Line:{0}  FAILED  Expected '{1}', but got '{2}'."
               .format(linenum, expected, actual))
    print(msg)


def test_b_dist_Eq(op_list):
    test(b_dist(op_list[0], 'a', 'b'), 1)
    test(b_dist(op_list[0], 'aac', 'bbg'), 6)


if __name__ == '__main__':
    op_list = [
        ast.parse("'a'=='b'").body[0].value.ops[0],     # type == ast.Eq
        ast.parse("'a' + 'b'").body[0].value.op,         # type == ast.Add
        ast.parse("'a' in 'b'").body[0].value.ops[0]       # type == ast.In
    ]

    test_b_dist_Eq(op_list)