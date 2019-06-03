li={} #dict 

def compUpdate(li, key, val):
    if not bool(li) or key not in li:
        li[key] = val
    else:
        if li[key] > n:
            li[key] = n
            return li
        else:
            return li

#compUpdate(li, 'a', 3)

print(li is not None, li)