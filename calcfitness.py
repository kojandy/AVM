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
    if type(op) == ast.In:
        return


def normalise(n):
    return 1 - 1.001**(-n)


def str_to_ordinal_value(s):
    numCharacter = 36   # alphanumeric with case insensitive
    v = 0
    for i in range(len(s)):
        v += numCharacter ** (len(s) - i - 1) * (ord(s[i])-96)
    return v


def test(actual, expected):
    import sys
    linenum = sys._getframe(1).f_lineno  # get the caller's line number.
    if (expected == actual):
        msg = "Line:{0}  PASS".format(linenum)
    else:
        msg = ("Line:{0}  FAILED  Expected '{1}', but got '{2}'."
               .format(linenum, expected, actual))
    print(msg)


def test_b_dist_eq(op):
    test(b_dist(op, 'a', 'b'), 1)
    test(b_dist(op, 'aac', 'bbg'), 6)


def test_str_to_ordinal_value():
    test(str_to_ordinal_value("abc"), 1*36*36 + 2*36 + 3)


if __name__ == '__main__':
    op_list = [
        ast.parse("'a'=='b'").body[0].value.ops[0],         # type == ast.Eq

        ast.parse("'a'>'b'").body[0].value.ops[0],          # type == ast.Gt
        ast.parse("'a'>='b'").body[0].value.ops[0],         # type == ast.GtE
        ast.parse("'a'<'b'").body[0].value.ops[0],          # type == ast.Lt
        ast.parse("'a'<='b'").body[0].value.ops[0]          # type == ast.LtE
    ]

    # test_b_dist_eq(op_list[0])
    test_str_to_ordinal_value()
