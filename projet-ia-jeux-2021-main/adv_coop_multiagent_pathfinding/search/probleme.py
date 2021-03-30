# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import functools
import time
import math
import random

#import search.grid2D
def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2) 


def legal_position(row,col,grid):


    return ( row>=0 and row<len(grid) and col>=0 and col<len(grid[0]) and grid[row][col]  )
    
###############################################################################

class Probleme(object):
    """ On definit un probleme comme étant: 
        - un état initial
        - un état but
        - une heuristique
        """
        
    def __init__(self,init,but,heuristique):
        self.init=init
        self.but=but
        self.heuristique=heuristique
        
    @abstractmethod
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        pass
        
    @abstractmethod    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            """
        pass
        
    @abstractmethod
    def successeurs(self,etat):
        """ retourne une liste avec les successeurs possibles
            """
        pass
        
    @abstractmethod
    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        pass
    
    



###############################################################################

@functools.total_ordering # to provide comparison of nodes
class Noeud:
    def __init__(self, etat, g, pere=None):
        self.etat = etat
        self.g = g
        self.pere = pere
        
    def __str__(self):
        #return np.array_str(self.etat) + "valeur=" + str(self.g)
        return str(self.etat) + " valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self,p):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Noeud(s,self.g+p.cost(self.etat,s),self) for s in p.successeurs(self.etat)]
        return nouveaux_fils
        
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
            """
        nouveaux_fils = self.expand(p)
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand(p)[k-1]
            
    def trace(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        while n!=None :
            print (n)
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return            
        

class ProblemeGrid2D(Probleme): 
    """ On definit un probleme de labyrithe comme étant: 
        - un état initial
        - un état but
        - une grid, donné comme un array booléen (False: obstacle)
        - une heuristique (supporte Manhattan, euclidienne)
        """ 
    def __init__(self,init,but,grid,heuristique):
            self.init=init
            self.but=but
            self.grid=grid
            self.heuristique=heuristique
        
    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            toujours 1 pour le taquin
            """
        return 1
        
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        return (self.but==e)
        
    def estObstacle(self,e):
        """ retorune vrai si l'état est un obsacle
            """
        return (self.grid[e]==False)
        
    def estDehors(self,etat):
        """retourne vrai si en dehors de la grille
            """
        (s,_)=self.grid.shape
        (x,y)=etat
        return ((x>=s) or (y>=s) or (x<0) or (y<0))

    
        
    def successeurs(self,etat):
            """ retourne des positions successeurs possibles
                """
            current_x,current_y = etat
            d = [(0,1),(1,0),(0,-1),(-1,0)]
            etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        s=""
        (x,y)= etat
        s+=str(x)+'_'+str(y)
        return s
        
    def h_value(self,e1,e2):
        """ applique l'heuristique pour le calcul 
            """
        if self.heuristique=='manhattan':
            h = distManhattan(e1,e2)
        elif self.heuristique=='uniform':
            h = 1
        return h


        
###############################################################################
# A*
###############################################################################

def astar(p,verbose=False,stepwise=False):
    """
    application de l'algorithme a-star
    sur un probleme donné
        """
        
    startTime = time.time()

    nodeInit = Noeud(p.init,0,None)
    frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

    reserve = {}        
    bestNoeud = nodeInit
    
    while frontiere != [] and not p.estBut(bestNoeud.etat):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique        
        
        if p.immatriculation(bestNoeud.etat) not in reserve:            
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value(n.etat,p.but)
                heapq.heappush(frontiere, (f,n))

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
        stop_stepwise=""
        if stepwise==True:
            stop_stepwise = input("Press Enter to continue (s to stop)...")
            print ("best", min_f, "\n", bestNoeud)
            print ("Frontière: \n", frontiere)
            print ("Réserve:", reserve)
            if stop_stepwise=="s":
                stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
    if verbose:
        bestNoeud.trace(p)          
        print ("=------------------------------=")
        print ("Nombre de noeuds explorés", len(reserve))
        c=0
        for (f,n) in frontiere:
            if p.immatriculation(n.etat) not in reserve:
                c+=1
        print ("Nombre de noeuds de la frontière", c)
        print ("Nombre de noeuds en mémoire:", c + len(reserve))
        print ("temps de calcul:", time.time() - startTime)
        print ("=------------------------------=")
     
    n=bestNoeud
    path = []
    while n!=None :
        path.append(n.etat)
        n = n.pere
    return path[::-1] # extended slice notation to reverse list


###############################################################################
# AUTRES ALGOS DE RESOLUTIONS...
###############################################################################

def randomwalk(g,posPlayers,j):

    """ algorithme de déplacement aléatoire"""
    
    row,col = posPlayers[j]
    g2=copy.deepcopy(g)
    liste=[(0,1),(0,-1),(1,0),(-1,0)]
    random.shuffle(liste)

    for x_inc,y_inc in liste: 
        
        if legal_position(row+x_inc,col+y_inc,g2) and (row+x_inc,col+y_inc) not in posPlayers:
            row+=x_inc
            col+=y_inc
            break
    posPlayers[j]=row,col
    
    return row,col


def astarv2(g,path,j,i,posPlayers,objectifs):

    """ retourne le chemin selon l'algorithme de déplacement local repair A*"""

    g2=copy.deepcopy(g)
    z=0                   #compteur de tentatives


    while(path[j][i] in posPlayers and i!=0):
                   
        
        z+=1

        # si on est déjà sur son objectif ou que toutes les possibilités ont été testées, on reste immobile un tour
        if(path[j][i]==objectifs[j] or z==5):
            c=posPlayers[j]
            path[j].insert(i,c)
            
            break

        # si on rencontre un obstacle, on met à jour la grille
        if(path[j][i]!=posPlayers[j]):
            g2[path[j][i]]=False

        # recalcul de ProblemeGrid2D
        p2=ProblemeGrid2D(posPlayers[j],objectifs[j],g2,'manhattan')
        
        
        # recalcul du chemin avec l'algorithme A*
        path2=astar(p2)
        path2=path2[1:]

        # Pour qu'en sortie de fonction le chemin soit fonctionnel, on le remplit de 0 jusqu'à l'itération actuelle
        path[j]=[]
        for k in range(0,i):
            path[j].append(0)
                
        for l in path2:
            path[j].append(l)
    

        # si on a rien rajouté par rapport au chemin initial, on reste sur place
        if(len(path2)==0):
            c=posPlayers[j]
            
            path[j].append(c)
            path[j].append(c)
            break


    return path[j]



def coopa(g,j,k,posPlayers,path,objectifs,i):

    """ retourne le chemin selon l'algorithme Hierarchical Cooperative A* d'un agent j qui veut éviter un agent k"""

    reserve=[]                  # Positions déjà testées
    frontiere=[posPlayers[j]]   # Positions à tester

    z=0                         # compteur de tentative

    g2=copy.deepcopy(g)
    path2=path[k][i:]           # on récupère le chemin qu'il reste à parcourir à k

    while(True):    
        tmp=[]                  # liste qui conserve les éléments de la frontière pour n+1
        random.shuffle(frontiere) # mélange aléatoire de la frontière
        z+=1

        # si on ne trouve pas de solution après un certain temps, on arrête de chercher
        if(z==100):
            print("limite dépassée")
            break

        # on parcourt la frontière
        for k in range(0,len(frontiere)):
            
            row,col=frontiere[k]
            if(legal_position(row, col, g) and (row,col) not in posPlayers and (row,col) not in reserve):

                # si un élément de la frontière est une position légale ou il n'y a pas d'autres joueurs et qui n'a pas
                # été explorée, soit elle est sur le chemin de k et on l'ajoute à la frontière à n+1, soit c'est la
                # case qu'on recherche

                if((row,col) in path2):
                    tmp.append((row,col))

                else:

                    # Lorsqu'une issue est trouvée, on calcule le chemin jusqu'à cette case, puis le chemin de cette 
                    # case jusqu'à l'objectif, ce sera le nouveau chemin de l'agent j
                    p=ProblemeGrid2D(posPlayers[j], (row,col), g2, 'manhattan')
                    p2=ProblemeGrid2D((row,col), objectifs[j], g2, 'manhattan')
                    pathj=astar(p)+astar(p2)
                    return pathj

            # On ajoute les positions possibles depuis la frontière n à la frontière n+1
            for s in successeurs(frontiere[k],g,posPlayers):
                tmp.append(s)

            reserve.append(frontiere[k])
        frontiere=tmp


    return [posPlayers[j]]+path[j][i:]

def successeurs(etat,g,posPlayers):
    """ Retourne les positions possibles depuis un état dans une grille"""

    res=[]
    liste=[(0,1),(0,-1),(1,0),(-1,0)]
    row,col=etat
    for x,y in liste:
        if(legal_position(row+x, col+y, g) and (row+x, col+y) not in posPlayers):
            res.append((row+x, col+y))
    return res

    path=[]
    return path


def localoptimum(posPlayers,objectifs,j,g):

    """ retourne la prochaine position de l'agent j qui le rapproche le plus de son objectif, ou random s'il est bloqué"""

    # on récupère les coordonnées de l'agent j et de son objectif, puis on fait la distance de manhattan
    next_row,next_col=posPlayers[j]
    x2,y2=objectifs[j]
    maxd=distManhattan((x2,y2),(next_row,next_col))
    maxi=(0,0)
    liste=[(0,1),(0,-1),(1,0),(-1,0)]
    random.shuffle(liste)

    # parmi les déplacements possibles, s'il y en a un qui à une meilleure distance de manhattan que le max actuel, il devient le max
    for xi,yi in liste:
        if(distManhattan((x2,y2),(next_row+xi,next_col+yi))<maxd and legal_position(next_row+xi,next_col+yi,g) and (next_row+xi,next_col+yi) not in posPlayers):
            maxd=distManhattan((x2,y2),(next_row+xi,next_col+yi))
            maxi=(xi,yi)
            
    # s'il n'y a pas de meilleure position que la position actuelle, on bouge au hasard

    if(maxi==(0,0)):
        return randomwalk(g, posPlayers, j)
            
    xi,yi=maxi
    next_row+=xi
    next_col+=yi
    
    return next_row,next_col


    
