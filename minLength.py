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

# op: ==, in
# 한 쪽 스트링, 다른 쪽 arg 인 경우에 대해서
# arg 만 슬라이싱 될 수 있음. exec 쓰면 해결 가능
class ChangeIf(TreeWalk):
    def pre_body_name(self):
        body = self.cur_node
        for i, child in enumerate(body[:]):
            self.walk(child)            
            if isinstance(child, ast.If):
                op = body[i].test.ops[0]                
                if isinstance(op,ast.Eq):   # op: ==               
                    lhs = body[i].test.left                 # * == *' 에서 *
                    rhs = body[i].test.comparators[0]       # * == *' 에서 *'
                    #yes slicing to arg
                    if isinstance(lhs, ast.Subscript) or isinstance(rhs, ast.Subscript):    # somewhere sliced                        
                        if isinstance(lhs, ast.Str) and isinstance(rhs.value, ast.Name):# 오른쪽이 파라미터
                            if isinstance(rhs.slice, ast.Index):                  # "a" == a[3]
                                n = rhs.slice.value.n + 1
                                li = compUpdate(li, rhs.s, n)
                            elif isinstance(rhs.slice, ast.Slice):                # "abba" == a[1:5]
                                upper = rhs.slice.upper.n
                                n = upper
                                li = compUpdate(li, rhs.s, n)
                        elif isinstance(rhs, ast.Str) and isinstance(lhs.value, ast.Name):     # a[2] == "abc"
                            n = len(rhs.s)
                            li = compUpdate(li, lhs.value.id, n) 
                    # no slicing to arg
                    else:       
                        if isinstance(lhs, ast.Str) or isinstance(rhs, ast.Str):
                            if isinstance(lhs, ast.Str) and isinstance(rhs, ast.Name):
                                n = len(lhs.s)
                                li = compUpdate(li, lhs.id, n)
                            elif isinstance(rhs, ast.Str) and isinstance(lhs, ast.Name):
                                n = len(rhs.s)
                                li = compUpdate(li, rhs.id, n)                   
                else:                       # op: in
                    lhs = body[i].test.left.s           # 'abcde' 같은 것            
                    rhs = body[i].test.comparators[0]   #.id 해야 파라미터 나옴
                    # yes slicing
                    if isinstance(lhs, ast.Subscript) or isinstance(rhs, ast.Subscript)
                        if isinstance(rhs, ast.Name):
                            if isinstance(rhs.slice, ast.Index):      # "a" in a[2]
                                n = rhs.slice.value.n + 1
                                li = compUpdate(li, rhs.value.id, n)
                            elif isinstance(rhs.slice, ast.Slice):    # "a" in a[2:4]
                                upper = rhs.slice.upper.n
                                #lower = rhs.slice.lower.n
                                n = upper
                                li = compUpdate(li, rhs.value.id, n)
                            else:                                           # "abb" in a
                                n = len(lhs)
                                li = compUpdate(li, rhs.value.id, n)
                    # no slicing
                    else: 
                        n = len(lhs)
                        li = compUpdate(li, rhs.id, n)
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