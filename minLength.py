# input: .py - target function
# output: integer - minimum length of string input
import astor
from tree_walk import * 

def fun(a, b, c):
    if a == 100:
        if a < b:
            if c == 0:
                pass
            if b < c:
                pass

class ChangeIf(TreeWalk):
    def pre_body_name(self):
        body = self.cur_node
        for i, child in enumerate(body[:]):
            self.walk(child)
            if isinstance(child, ast.If):
                count.incr()
                lhs = body[i].test.left.id
                op = body[i].test.ops[0]
                rhs = body[i].test.comparators[0]
                depth = count.getCount()
                traceFunction = trace.whichTracetoUse(op, lhs, rhs)
                args1 = ast.Num()
                args1.n = depth
                args2 = ast.Str(lhs)
                args3 = rhs
                body[i].test = ast.Call(ast.Name("traceFunction"), [args1, args2, args3], [])
        return True

    def pre_Call(self):
        self.__name = self.cur_node.func.id
        return True

walker = ChangeIf()
walker.walk(_ast)


def minLength(f):
    _ast = astor.code_to_ast(f)
