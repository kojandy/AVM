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
    if "abc" in a:
        if "a" in b:
            if "ab" in c:
                pass
            if "ac" in c:
                pass
li=[] #list that contain numbers

class ChangeIf(TreeWalk):
    def pre_body_name(self):
        body = self.cur_node
        for i, child in enumerate(body[:]):
            self.walk(child)
            #if child contains concat:
            #    break
            if isinstance(child, ast.If):
                lhs = body[i].test.left.s # in order to cover "in" operator, 양쪽 다 변수인 경우 생각 해야함.
                #op = body[i].test.ops[0] == "In()"
                #rhs = body[i].test.comparators[0] # if a <someop> "abc"
                n = len(lhs)
                li.append(n)
        return True

    def pre_Call(self):
        self.__name = self.cur_node.func.id
        return True

def minLength(f):
    _ast = astor.code_to_ast(f)
    walker = ChangeIf()
    walker.walk(_ast)
    print (li)

minLength(fun)