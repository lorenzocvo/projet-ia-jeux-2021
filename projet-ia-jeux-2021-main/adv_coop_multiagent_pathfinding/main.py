# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain
import copy

import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme




# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----




# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()


def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'exAdvCoopMap'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
    
def main():

    
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)



    if(len(sys.argv)==3):
        init(str(sys.argv[2]))
    else:
        init()
    
    
    blocage=0  # avancer au tour par tout si 1, en continu sinon

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize
       
    print("lignes", nbLignes)
    print("colonnes", nbCols)

    
    players = [o for o in game.layers['joueur']]
    print(players)
    nbPlayers = len(players)
    score = [0]*nbPlayers
    
       
           
    # on localise tous les états initiaux (loc du joueur)
    # positions initiales des joueurs
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    # sur le layer ramassable
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    # sur le layer obstacle
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    print ("Wall states:", wallStates)
    
    def legal_position(row,col):
        # une position legale est dans la carte et pas sur un mur
        return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols
        
    #-------------------------------
    # Attributaion aleatoire des fioles 
    #-------------------------------
    
    objectifs = goalStates
    #random.shuffle(objectifs)
    
    

    for i in range(0,len(players)):
        print("Objectif joueur "+str(i),objectifs[i])


    team=[]                         # liste d'attribution d'équipe pour chaque agent
    for i in range(len(players)):
        if(i%2==0):
            team.append(0)
        else:
            team.append(1)

    #random.shuffle(team)            #equipes tirées au hasard



    scoreteam0=0         # score de l'equipe 0 -> nombre d'agents arrivés à leur objectif
    scoreteam1=0         # score de l'equipe 1 -> nombre d'agents arrivés à leur objectif

    # les scores pos des équipes servent à les départager en cas d'égalité de score, le plus petit score pos l'emporte

    scoreposteam0=0      # itérations de l'équipe 1 -> nombre d'itérations effectués par les agents de l'équipe 0 avant d'atteindre leur objectif
    scoreposteam1=0      # itérations de l'équipe 1 -> nombre d'itérations effectués par les agents de l'équipe 1 avant d'atteindre leur objectif

    # priorités utilisées dans l'algorithme Hierchical A*

    prioteam0=len(players)   # priorité courante de l'équipe 0 (len(players) si pas de priorité en cours)
    prioteam1=len(players)   # priorité courante de l'équipe 0 (len(players) si pas de priorité en cours)

    # attentes utilisées dans l'algorithme Hierarchical A*

    attente0=[]              # agents actuellement en attente dans l'équipe 0
    attente1=[]              # agents actuellement en attente dans l'équipe 1


    # liste des stratégies, attribuées plus tard
    strategie=[-1 for i in range(0,len(players))]

    
    
    # preset des cartes pour le notebook de rendu
    
    if(len(sys.argv)==3):

        if(sys.argv[2]=='carte2' or sys.argv[2]=='carte3' or sys.argv[2]=='carte5'):
            for i in range(0,len(players)):
                strategie[i]=0


        elif(sys.argv[2]=='carte9'):
            strategie[0]=0
            strategie[1]=0
            z=objectifs[0]
            objectifs[0]=objectifs[1]
            objectifs[1]=z

        elif(sys.argv[2]=='carte10'):
            for i in range(0,len(players)):
                strategie[i]=2

            team[0]=0
            team[1]=0
            team[2]=0
            team[3]=1

            z=objectifs[0]
            objectifs[0]=objectifs[1]
            objectifs[1]=z
            
            z=objectifs[2]
            objectifs[2]=objectifs[3]
            objectifs[3]=z

        elif(sys.argv[2]=='carte7'):
            strategie[0]=1

        elif(sys.argv[2]=='carte11'):
            for i in range(0,len(players)):
                strategie[i]=1

            team[0]=0
            team[1]=0
            team[2]=0
            team[3]=1

            z=objectifs[0]
            objectifs[0]=objectifs[1]
            objectifs[1]=z
            
            z=objectifs[2]
            objectifs[2]=objectifs[3]
            objectifs[3]=z

        elif(sys.argv[2]=='carte12'):
            
            strategie[i]=1


        # 2 joueurs exemple Hierarchical Cooperative A*

        elif(sys.argv[2]=='carte8'):
            strategie[0]=2
            strategie[1]=2
            z=objectifs[0]
            objectifs[0]=objectifs[1]
            objectifs[1]=z
            team[0]=team[1]
        else:
            random.shuffle(team)
            random.shuffle(objectifs)
            for i in range(0,len(players)):
                if(team[i]==0):
                    strategie[i]=0
                else:
                    strategie[i]=2



    # exemple de confrontation entre la stratégie Local repair A* et Hierarchilal Cooperative A* 

    else:
        random.shuffle(team)
        random.shuffle(objectifs)
        for i in range(0,len(players)):
            if(team[i]==0):
                strategie[i]=0
            else:
                strategie[i]=2



    
    
    g = np.ones((nbLignes, nbCols),dtype=bool)  # par defaut la matrice comprend des True  
    for w in wallStates:            # putting False for walls
        g[w] = False
    
    # Calcul des chemins pour les algortihmes A* (Local repair A* et Hierarchical A*)
    path = []
    for i in range(0, len(players)):
        if(strategie[i]%2 == 0):    # Les algorithmes A* sont les stratégies 0 et 2
            p = ProblemeGrid2D(initStates[i],objectifs[i],g,'manhattan')
            path.append(probleme.astar(p))        # calcul du chemin de l'agent i
            print ("Chemin trouvé:", path[i])
        else: 
            path.append(0)        # si l'algorithme n'est pas A*, on met un 0 dans son path
    

    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
    
    posPlayers = initStates    # Etats initiaux

    fin=[]                     # Liste des agents ayant atteint leur objectif

    for i in range(iterations):
        
        # on fait bouger chaque joueur séquentiellement

        for j in range(0,len(path)):

            # un agent qui a atteint son objectif ne bouge plus, quelque soit sa stratégie

            if(j not in fin):

            
                # 1e stratégie : Local Repair A*

                if(strategie[j]==0):

                    # on vérifie que le prochain mouvement de j est bloqué par un joueur avant de modifier son chemin

                    if(path[j][i] in posPlayers and i!=0):
                        print("Changement de direction")
                        path[j]=probleme.astarv2(g,path,j,i,posPlayers,objectifs)

                    posPlayers[j]=path[j][i]

                
                # 2e stratégie Local optimum

                if(strategie[j]==1):
                    g2=copy.deepcopy(g)
                    posPlayers[j]=probleme.localoptimum(posPlayers,objectifs,j,g2)

                # 3e stratégie : Hierarchical Cooperative A*

                if(strategie[j]==2):
                    
                    # s'il n'y a plus d'agent de l'équipe 0 en attente, on réinitialise la priorité de l'équipe 0

                    if(len(attente0)==0):
                        prioteam0=len(players)

                    # s'il n'y a plus d'agent de l'équipe 1 en attente, on réinitialise la priorité de l'équipe 1

                    if(len(attente1)==0):
                        prioteam1=len(players)

                    # on vérifie que le prochain mouvement de j est bloqué par un joueur avant de modifier son chemin

                    if(path[j][i] in posPlayers and i!=0):

                        # on récupère l'indice du joueur qui bloque

                        for k in range(0,len(posPlayers)):
                            if(posPlayers[k]==path[j][i]):
                                break

                        # si le joueur n'est pas de la même équipe on ne bouge pas, même chose si on est prioritaire par 
                        # rapport à un autre joueur de son équipe (indice plus petit) 

                        if(team[k]!=team[j] or j<k ):
                        #if(team[k]!=team[j]):
                            path[j].insert(i,posPlayers[j])

                        # si le joueur est de la même équipe et que l'agent j n'est pas prioritaire, alors on change son chemin

                        else:
                            if(j>k):

                                print("Changement de direction")
                                
                                path[j]=path[j][:i]+probleme.coopa(g,j,k,posPlayers,path,objectifs,i)

                                # on met à jour la priorité
                                
                                if(team[j]==1):
                                    prioteam1=k
                                else:
                                    prioteam0=k

                            # si l'agent n'a pas la priorité (bouchon), il se décale aussi même si son voisin direct est moins prioritaire
                            # que lui
                            
                            if(team[j]==0 and j>prioteam0):
                                path[j]=path[j][:i]+probleme.coopa(g,j,k,posPlayers,path,objectifs,i)

                            if(team[j]==1 and j>prioteam1):
                                path[j]=path[j][:i]+probleme.coopa(g,j,k,posPlayers,path,objectifs,i)

                    # si le chemin n'est plus bloqué, on vérifie bien que l'agent j est sorti du chemin de l'agent prioritaire pour 
                    # mettre à jour l'attente de son équipe

                    if(team[j]==0 and prioteam0<len(players)):
                        if(path[j][i-1] in path[prioteam0] and path[j][i] not in path[prioteam0]):
                            attente0-=1

                    if(team[j]==1 and prioteam1<len(players)):
                        
                        if(i>1 and path[j][i-1] in path[prioteam1] and path[j][i] not in path[k]):
                            attente1-=1

                    posPlayers[j]=path[j][i]


                # mise à jour de la position de l'agent j dans posPlayers et sur l'interface graphique

                row,col=posPlayers[j]
                players[j].set_rowcol(row,col)
                print ("pos "+str(j)+" : ", row,col)

                # si l'agent j a atteint son objectif, on l'immobilise et on met à jour son score et celui de son équipe

                if(posPlayers[j]==objectifs[j]):
                    score[j]=1
                    fin.append(j)
                    print("le joueur "+str(j)+" a atteint son but!")
                    if(team[j]==0):
                        scoreteam0+=1
                    else:
                        scoreteam1+=1


        # on vérifie si une des équipes a gagné        
        
        if(scoreteam0>=len(players)/2):
            print("L'équipe 0 a gagné")
            
            break

        # s'il y a un nombre de joueurs impairs, il y aura un joueur de l'équipe 1 en moins, on prend ça en compte pour vérifier
        # si l'équipe 1 a gagné
        
        if(len(players)%2==0):
            if(scoreteam1==len(players)/2):
                print("L'équipe 1 a gagné")
                
                break
        else:
            if(scoreteam1+1==len(players)/2):
                print("L'équipe 1 a gagné")
                
                break


        # pour chaque équipe, chaque joueur encore en chemin vers son objectif lui rajoute un point dans scorepos

        for j in range(0,len(players)):
            if(j not in fin):
                if(team[j]==0):
                    scoreposteam0+=1
                else:
                    scoreposteam1+=1



        if(blocage==1):
            event = pygame.event.wait()
            
            if event.type == pygame.KEYDOWN:
                blocage=1
            

        game.mainiteration()
        

        # on passe a l'iteration suivante du jeu
        

    # si les équipes n'ont pas pu se départager au score on les départage au scorepos, et s'il y a encore égalité, alors
    # c'est une égalité parfaite

    if(i==iterations-1):
        print("fin iteration")
        if(scoreteam0>scoreteam1):
            print("L'équipe 0 a gagné")
            
        elif(scoreteam0<scoreteam1):
            print("L'équipe 1 a gagné")
            

        else:
            if(scoreposteam0>scoreposteam1):
                print("L'équipe 0 a gagné")
                
            elif(scoreposteam0<scoreposteam1):
                print("L'équipe 1 a gagné")
                
            else:
                print("Egalité parfaite")


    print(team)
    
    print ("scores:", score)



    pygame.quit()
    
    
    
    
    #-------------------------------
    
        
 
   

 
    
   

if __name__ == '__main__':
    main()
    
     
        


