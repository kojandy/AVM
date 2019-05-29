# input: .py - target function
# output: integer - minimum length of string input
'''
1. if 문 안에 contains(n개의 캐릭터), else는 할 필요가 없음!!!
    --> n을 구한다. --> 변수와 비교하여 n이 더 크면 업데이트
2. if or body에서 concat 나오면 리턴 ㄱ ㄱ
'''

import astor
import ast
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
            if child contains concat:
                break
            if isinstance(child, ast.If):
                lhs = body[i].test.left.id
                op = body[i].test.ops[0]
                rhs = body[i].test.comparators[0]
                n = len(rhs)
                compUpdate(temp, n)
        return True

    def pre_Call(self):
        self.__name = self.cur_node.func.id
        return True

def minLength(f):
    _ast = astor.code_to_ast(f)
    walker = ChangeIf()
    walker.walk(_ast)
    __ast = astor.to_source(_ast)
    return __ast

minLength(fun)