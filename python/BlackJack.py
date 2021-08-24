# -*- coding: utf-8 -*-
from os import scandir
#from python.Servidor import ListPlayers
import socket, sys
import time
import random

HOST = '127.0.0.1'  # endereço IP
PORT = 20000        # Porta utilizada pelo servidor
BUFFER_SIZE = 1024  # tamanho do buffer para recepção dos dados


Player = []
resposta = []

def InfoPlayer():
    name = input("\n----> Digite seu nome: ")
    city = input("----> Digite sua cidade: ")
    p = AddPlayer("", name, city, 1000, 0, 0, 0, 0, "", [])
     

class AddPlayer:
    def __init__(self, code, name, city, amount, victories, numCards, punctuation, beting, eat, cards):
        self.code = code
        self.name = name
        self.city = city
        self.amount = amount
        self.victories = victories
        self.cards = cards
        self.punctuation = punctuation
        self.beting = beting
        self.eat = eat
        self.numCards = numCards

        Player.append([code, name, city, amount, victories, numCards, punctuation, beting, eat, cards])
        
def Bet(player):
    amountPlayer = int(player[0][3])
    value = int(input("Qual valor deseja apostar? \n----> "))
    while (value < 1 or value > amountPlayer):
        print("Não é permitido apostar esse valor")
        value = int(input("Qual valor deseja apostar? \n----> "))

    player[0][3] -= value
    player[0][7] = value
    
    return value


def treatment(player):
    print(player)
    player[9] = player[9][: - 1]
    player[0] = player[0][0:2]
                    
    #Transforma os numeros em int
    player[0] = int(player[0])
    player[3] = int(player[3])
    player[4] = int(player[4])
    player[5] = int(player[5])
    player[6] = int(player[6])
    player[7] = int(player[7])

    Player.clear()
    Player.append(player)


def eat():
    eating = input("----> Deseja comer uma nova carta ? [s/n] \n----> ")
    return eating


def main(argv): 
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            print("\n*********** BLACKJACK ***********\n")
            InfoPlayer()

            playerString = ",".join(str(v) for v in Player[0])

            s.connect((HOST, PORT))
            s.send(playerString.encode('utf-8')) #.encode - converte a string para bytes
            i = 0
            while(True):
                data = s.recv(BUFFER_SIZE)
                texto_string = data.decode('utf-8') #converte os bytes em string

                if texto_string == "1":
                    resposta = str(Bet(Player))
                    s.send(resposta.encode('utf-8'))
                
                elif texto_string == "2":
                    resposta = eat()
                
                elif len(texto_string) > 100:
                    player = texto_string.split(".")
                    eat(player)
                    resp = "-".join(str(v) for v in Player)
                    s.send(resp.encode('utf-8'))
                else:
                    print(texto_string)

                    
    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return


if __name__ == "__main__":   
    main(sys.argv[1:])
