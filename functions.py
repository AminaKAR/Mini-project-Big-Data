import urllib.request
import pandas as pd
import numpy as np
import json
import time

def indentify_turtle(turtle):
    speeds=list(turtle.diff()[1:]) # we differtiate position to get speed
    reg,msg=regular(speeds)
    if reg :
        return(reg,msg)
    cyc,msg=cyclic(speeds)
    if cyc :
        return(cyc,msg)
    
    
    dis,msg=distraite(speeds)
    return(dis,msg)

def regular(tab):
    std=pd.core.series.Series(tab).std()
    if std == 0:
        return(True,'Tortue régulière avec une vitesse : '+str(tab[0]))
    else:
        return(False,'0')

def distraite(tab):
    tab=pd.core.series.Series(tab)
    return(True,'Tortue distraite avec un max : '+str(tab.max())+' et un min : '+str(tab.min()))

def tired(speed):
    s=list(speed)
    if 0 not in s :
        return(False,'0')
    size = len(list(s)) 
    idx_list = [idx + 1 for idx, val in
                enumerate(s) if val == 0] 


    res = [s[i: j] for i, j in
            zip([0] + idx_list, idx_list + 
            ([size] if idx_list[-1] != size else []))] 


    res=(res[1:-1])
    nbrzero=0
    for i in res:
        tmp=pd.Series(i[:]).diff().diff().dropna()
        if len(list(tmp))-list(tmp).count(0)==3:
            nbrzero+=1

        if (nbrzero/(len(tmp)+1)) >0.8:
            return (True,'fatigué')
    return(False,'0')

def get_indices(elt,list_of_elts):
    import more_itertools as iter_tools 
    indices = list(iter_tools.locate(list_of_elts, lambda element: element == elt))
    return(indices)

def cyclic(speeds): 
    """ 
    a cycle has no begining and no end hence the speeds of the 
    cycle window won't be sorted like the server configuration
    we check the indices of an element , we assume its unicity in the cycle to avoid heavy computing
    if it's not the case we use an exhaustive search
    """
    indices=get_indices(speeds[0],speeds)
    if len(indices)<3:
        return False,'0' # we need at least three points to make two segments, this is due if the turtle is not cyclic or not enough data and no way to be  sure

    null_indices_std=pd.Series(indices).diff()[1:].std()==0 # we verify if the indices are evenly spaced, it's a heuristic if the elt is unique in the cycle, it's computationaly light and worth trying
    if null_indices_std :
        cycle=True
        for i in range(len(indices)-2):
            if speeds[indices[i]:indices[i+1]]!=speeds[indices[i+1]:indices[i+2]]:
                cycle=False
                break
        if cycle :
            return(True,'Tortue cyclique, le tableau des vitesses dans la fenêtre est : '+str(speeds[indices[0]:indices[1]]))
        #if it's True then it's cyclic, however if it's false we c'ant be sure if it's not cyclic or if the assumption of the element's unicity is wrong
      
    potential_cycles=[]
    for i in range (len(indices)):
        for j in range(i+1,len(indices)):
            #print('*'*5)
            #print(indices[i],indices[j],abs(indices[i]-indices[j]))
            long_seq_to_check=abs(indices[i]-indices[j])
            begining=indices[j]
            end=indices[j]+long_seq_to_check
            cycle=True
            while(end<len(speeds)):
                if(speeds[indices[i]:indices[j]]==speeds[begining:end]):
                    """print(True)
                    print(begining,end,speeds[begining:end],' == ',speeds[indices[i]:indices[j]])"""
                else:
                    break
                    cycle=False
                    """print(False)
                    print(begining,end,speeds[begining:end],' != ',speeds[indices[i]:indices[j]])"""

                begining=end
                end+=long_seq_to_check
            cycle and potential_cycles.append(speeds[indices[i]:indices[j]]) # si cycle est false we have a court circuit et cette instruction ne s'execute pas
    if (len(potential_cycles) == 0):
        return (False,'0')
    # we search the most compact cycle
    min_cyc=potential_cycles[0]
    min_=len(min_cyc)
    for c in potential_cycles:
        if len(c)<min_:
            min_=len(c)
            min_cyc=c
    return(True,'Tortue cyclique, le tableau des vitesses dans la fenêtre est : '+str(min_cyc))

