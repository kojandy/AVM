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
            # slicing이 있으면 .value가 붙는다!!!!
            if isinstance(child, ast.If):
                op = body[i].test.ops[0]                
                if isinstance(op,ast.Eq):   # op: ==               
                    lhs = body[i].test.left                 # * == *' 에서 *
                    rhs = body[i].test.comparators[0]       # * == *' 에서 *'
                    if isinstance(lhs.value, ast.Str) or isinstance(rhs.value, ast.Str):
                        if isinstance(lhs.value, ast.Str) and isinstance(rhs.value, ast.Name):       
                            if isinstance(rhs.value.slice, ast.Index):                  # "a" == a[3]
                                n = rhs.value.slice.n + 1
                                li = compUpdate(li, rhs.value.s, n)
                            elif isinstance(rhs.value.slice, ast.Slice):                # "abba" == a[1:5]
                                upper = body.value.slice.upper.n
                                n = upper
                                li = compUpdate(li, rhs.value.s, n)
                            else:                                                       # "abc" == a
                                n = len(lhs.value.s)                            
                                li = compUpdate(li, rhs.value.id, n)
                        elif isinstance(rhs.value, ast.Str) and isinstance(lhs.value, ast.Name):     # a == "abc"
                            n = len(rhs.value.s)
                            li = compUpdate(li, lhs.value.id, n)                            
                else:                       # op: in
                    lhs = body[i].test.left.value.s                     
                    rhs = body[i].test.comparators[0]
                    if isinstance(rhs, ast.Name):
                        if isinstance(rhs.value.slice, ast.Index):      # "a" in a[2]
                            n = rhs.value.slice.value.n + 1
                            li = compUpdate(li, rhs.value.s, n)
                        elif isinstance(rhs.value.slice, ast.Slice):    # "a" in a[2:4]
                            upper = body.value.slice.upper.n
                            #lower = body.value.slice.lower.n
                            n = upper
                            li = compUpdate(li, rhs.value.s, n)
                        else:                                           # "abb" in a
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