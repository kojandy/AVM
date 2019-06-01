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
    if "abcddddd" in a:
        if "ddddda" in b:
            if "abdd" in c:
                pass
            if c == "abc":
                pass

li={} #dict 

def compUpdate(li, key, val):
    if li[key] > n:
        li[key] = n
        return li
    else:
        return li

class ChangeIf(TreeWalk):
    def pre_body_name(self):
        body = self.cur_node
        for i, child in enumerate(body[:]):
            self.walk(child)
            #if child contains concat:
            #    break
            if isinstance(child, ast.If):
                op = body[i].test.ops[0]                
                if isinstance(op,ast.Eq):   # ==               
                    lhs = body[i].test.left
                    rhs = body[i].test.comparators[0]
                    if isinstance(lhs, ast.Str) or isinstance(rhs, ast.Str):
                        if isinstance(lhs, ast.Str) and isinstance(rhs, ast.Arg):
                            n = len(lhs.s)                            
                            li = compUpdate(li, rhs, n)
                        elif isinstance(rhs, ast.Str) and isinstance(lhs, ast.Arg):
                            n = len(rhs.s)
                            li = compUpdate(li, lhs, n)                            
                else:                       # in
                    lhs = body[i].test.left.s 
                    rhs = body[i].test.comparators[0]
                    n = len(lhs)
                    li = compUpdate(li, rhs, n)
                    
        return True

    def pre_Call(self):
        self.__name = self.cur_node.func.id
        return True

def minLength(f):
    _ast = astor.code_to_ast(f)
    walker = ChangeIf()
    walker.walk(_ast)
    return li

print( minLength(fun) )