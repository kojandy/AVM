# input: .py - target function
# output: integer - minimum length of string input

import astor
import ast
from tree_walk import * 


def fun(a, b, c):
    if "abcddddd" in a[2:4]:
        if "ddddda" in b[6]:
            if "abdd" in c:
                pass
            if c[3:6] == "abc":
                pass

li=dict() #dict 

def compUpdate(li, key, val):
    if bool(li) and key in li:
        if li[key] < val:       #replace to bigger one
            li[key] = val
            return li
        else:                   #don't replace
            return li
    else:
        if li is not None: 
            li[key] = val            
            return li

# op: ==, in
# 한 쪽 스트링, 다른 쪽 arg 인 경우에 대해서
# arg 만 슬라이싱 될 수 있음. exec 쓰면 해결 가능
class ChangeIf(TreeWalk):
    def pre_body_name(self):
        global li
        body = self.cur_node
        for i, child in enumerate(body[:]):
            self.walk(child)            
            if isinstance(child, ast.If):
                op = body[i].test.ops[0]   
                print(op)             
                if isinstance(op,ast.Eq):   # op: ==                         
                    lhs = body[i].test.left                 # * == *' 에서 *
                    rhs = body[i].test.comparators[0]       # * == *' 에서 *'                    
                    #yes slicing to arg
                    if isinstance(lhs, ast.Subscript) or isinstance(rhs, ast.Subscript):    # somewhere sliced                        
                        if isinstance(lhs, ast.Str) and isinstance(rhs.value, ast.Name):# 오른쪽이 파라미터
                            if isinstance(rhs.slice, ast.Index):                  # "a" == a[3]
                                n = rhs.slice.value.n + 1                                
                                li = compUpdate(li, rhs.value.id, n)
                            elif isinstance(rhs.slice, ast.Slice):                # "abba" == a[1:5]                                
                                upper = rhs.slice.upper.n
                                n = upper                                
                                li = compUpdate(li, rhs.value.id, n)
                        elif isinstance(rhs, ast.Str) and isinstance(lhs.value, ast.Name):     # a[2] == "abc"
                            n = len(rhs.s)
                            li = compUpdate(li, lhs.value.id, n) 
                    # no slicing to arg
                    else:       
                        if isinstance(lhs, ast.Str) or isinstance(rhs, ast.Str):                            
                            if isinstance(lhs, ast.Str) and isinstance(rhs, ast.Name):      # 오른쪽이 파라미터                                
                                n = len(lhs.s)
                                li = compUpdate(li, rhs.id, n)                                
                            elif isinstance(rhs, ast.Str) and isinstance(lhs, ast.Name):    # 왼쪽이 파라미터
                                n = len(rhs.s)
                                li = compUpdate(li, lhs.id, n)                   
                else:                                       # op: in                    
                    lhs = body[i].test.left.s               # 'abcde' 같은 것            
                    rhs = body[i].test.comparators[0]       #.id 해야 파라미터 나옴
                    # yes slicing
                    if isinstance(lhs, ast.Subscript) or isinstance(rhs, ast.Subscript):                        
                        if isinstance(rhs.value, ast.Name):
                            if isinstance(rhs.slice, ast.Index):      # "a" in a[2]
                                n = rhs.slice.value.n + 1                                
                                print(rhs.value.id)
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