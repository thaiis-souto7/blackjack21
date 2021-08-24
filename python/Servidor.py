# -*- coding: utf-8 -*-
from os import scandir
import socket, sys
from threading import Thread
import random, time

HOST = '127.0.0.1'  # endereço IP
PORT = 20000        # Porta utilizada pelo servidor
BUFFER_SIZE = 1024  # tamanho do buffer para recepção dos dados

ListPlayers = []
valueRound = 0
clients = 0
Ordem = []
resposta = ""

"""
    1 - Qual valor deseja apostar?
"""

#Pergunta quanto que o jogador quer apostar e faz a aposta
def Bet(player):
    print(player)
    str2 = 'Carteira: R$ {}'.format(player[3])
    str = "1"
    clientsocket = ""
    for i in range(len(Ordem)):
        if player[1] == Ordem[i][0]:
            clientsocket = Ordem[i][1]
    clientsocket.send(str.encode('utf-8'))
    clientsocket.send(str2.encode('utf-8'))
    time.sleep(10)
    
    player[7] = int(resposta)
    player[3] -= player[7]
    global valueRound
    valueRound += player[7]
    print(player)
    return player
       

#Reseta o baralho já o embaralhando
def ResetCheap():
    cards = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]*4
    random.shuffle(cards)
    return cards

#Distribui as duas cartas iniciais aos jogadores
def GiveCards(cheap):
    print(ListPlayers)
    for i in range(len(ListPlayers)):
        cards = []
        cards.append(cheap[0])
        cards.append(cheap[1])
            
        ListPlayers[i][9] = cards

        del(cheap[0:2])



def eat(player,cheap):
    while(True):
        #Envia a lista do player com as cartas atuais
        str = 'Cartas: {} \nValor Atual: {}'.format(player[9], CountCards(player[9]))
        str2 = "2"
        clientsocket = ""
        for i in range(len(Ordem)):
            if player[1] == Ordem[i][0]:
                clientsocket = Ordem[i][1]
        clientsocket.send(str.encode('utf-8'))
        clientsocket.send(str2.encode('utf-8'))
        time.sleep(15)

        if player[6] == 21:
            str = '\nVocê já tem 21!\n---------------------------------\n'
            print(str)
            clientsocket.send(str.encode('utf-8'))
            break
        elif player[6] > 21:
            str = '\nVocê estourou!\n---------------------------------\n'
            print(str)
            clientsocket.send(str.encode('utf-8'))
            break
        else:    
            print(resposta,"BATATAAAAAAAAAAAA")
            if(resposta == "s"):
                print("CARDSSSS", player[9])
                cards = player[9]
                print("CARDSSSS CHEAPPP", cheap[0])
                cards.append(cheap[0])
                player[9] = cards
                del(cheap[0:1])
                print("\nCartas: ", player[9], "\nValor Atual: ", CountCards(player[9]))
                player[6] = CountCards(player[9])
            else:
                break
    return player


#Mostra o total de cartas que tem na mão do jogador
def CountCards(cards):

    sum = 0
    for i in range(len(cards)):
        #Considera o A como 11 caso tenha um K Q J ou 10
        if cards[i] == "A":
            for j in range(len(cards)):
                if cards[j] == "K" or cards[j] == "Q" or cards[j] == "J" or cards[j] == "10":
                    sum += 10
            sum += 1
        elif cards[i] == "2":
            sum += 2
        elif cards[i] == "3":
            sum += 3
        elif cards[i] == "4":
            sum += 4
        elif cards[i] == "5":
            sum += 5
        elif cards[i] == "6":
            sum += 6
        elif cards[i] == "7":
            sum += 7
        elif cards[i] == "8":
            sum += 8
        elif cards[i] == "9":
            sum += 9
        elif cards[i] == "10":
            sum += 10
        elif cards[i] == "J":
            sum += 10
        elif cards[i] == "Q":
            sum += 10
        elif cards[i] == "K":
            sum += 10
    
    #Trata caso o A esteja sendo considerado 11 e esteje estourando, ai passa ela para 1 denovo
    for i in range(len(cards)):
        if sum > 21:
            if cards[i] == "A":
                for j in range(len(cards)):
                    if cards[j] == "K" or cards[j] == "Q" or cards[j] == "J" or cards[j] == "10":
                        sum -= 10

    return sum

def win():

    large = 0
    blackjack = []
    codBlackjack = []
    codWinners = []
    winners = []
    points = []
    

    for i in range(len(ListPlayers)):
        
        points.append(ListPlayers[i][6])
        if points[i] > large and points[i] <= 21:
            large = points[i]
            winners.clear()
            codWinners.clear()
            winners.append(ListPlayers[i][1])
            codWinners.append(ListPlayers[i][0])
            
        elif points[i] == large:
            winners.append(ListPlayers[i][1])
            codWinners.append(ListPlayers[i][0])
            
        if points[i] == 21:
            for j in range(len(ListPlayers[i][9])):
                if ListPlayers[i][5][j] == "A":
                    blackjack.append(ListPlayers[i][1])
                    codBlackjack.append(ListPlayers[i][0])
                        

    global valueRound
    if len(blackjack) > 0:
        for i in range(len(blackjack)):
            ListPlayers[codBlackjack[i]-1][3] += valueRound/len(blackjack)
            ListPlayers[codBlackjack[i]-1][4] += 1
        print("TIVEMOS BLACKJACK")
        valueRound = 0
        return blackjack

    elif len(winners) > 0 :
        #Se tiver mais que um vencedor, vai dividir o lucro entre os dois e a vitoria para os dois tambem
        for i in range(len(winners)):
            ListPlayers[codWinners[i]-1][3] += valueRound/len(winners)
            ListPlayers[codWinners[i]-1][4] += 1
        valueRound = 0
        return winners

    #Caso ninguem tenha tido 21, da o valor total ao vencedor e a vitoria
    else:
        for i in range(len(ListPlayers)):
            ListPlayers[i][3] += valueRound/len(ListPlayers)
        valueRound = 0
        print("\nNão tivemos vencedores, todos estouraram! \nO valor foi redividido entre todos os jogadores!\n")
        return winners

    

#Mostra o montande de dinheiro que o jogador tem
def ShowAmount(player):
    print("Seu montante é   |",player[3])


#Controla o decorrer da rodada
def Round(numRound,cheap):
    print("\n\n*********** BLACKJACK ***********\n***********  ROUND ",numRound+1,"***********\n")
    
    for i in range(len(ListPlayers)):
        print("\nVez do jogador", ListPlayers[i][1])
        ShowAmount(ListPlayers[i])
        ListPlayers[i] = Bet(ListPlayers[i])
    
    #Entrega duas cartas para os jogadores
    GiveCards(cheap)
    
    #Da a opção de comer novamente ou não
    for i in range(len(ListPlayers)):
        print("\n_____ JOGADA _____")
        print("\nVez do jogador: ", ListPlayers[i][1])
        
        ListPlayers[i][6] = CountCards(ListPlayers[i][9])

        print("\nCartas: ", ListPlayers[i][9], "\nValor Atual: ", ListPlayers[i][6])
        ShowAmount(ListPlayers[i])
        ListPlayers[i] = eat(ListPlayers[i], cheap) 
        
    
    print("\n\n*********************************\n** O Vencedor foi: ", win(), "**\n*********************************")



def NewClient(clientsocket,addr):
    while True:
        try:
            global resposta
            numberOne = []
            data = clientsocket.recv(BUFFER_SIZE)
            if not data:
                print("Aguardando Cliente !!")
                time.sleep(5)

            print(data.decode())
            texto_recebido = data.decode('utf-8') # converte os bytes em string
            #TransforInPlayer(texto_recebido)
            print('recebido do cliente {} na porta {}: {}'.format(addr[0], addr[1],texto_recebido))
            
            print(texto_recebido,"FEIJAAAAAAOOOOOOOOOOOo")
            resposta = texto_recebido
            if texto_recebido == "s" or texto_recebido == "S" or texto_recebido == "sim" or texto_recebido == "SIM" or texto_recebido == "Sim":
                resposta = "s"
            elif texto_recebido == "n" or texto_recebido == "N" or texto_recebido == "nao" or texto_recebido == "NAO" or texto_recebido == "Nao":
                resposta = "n"
            elif len(texto_recebido) > 16:

                player = texto_recebido.split(",")
                player[0] = player[0][1:]
                player[9] = player[0][:-1]

                #Transforma os numeros em int
                player[0] = clients
                player[3] = int(player[3])
                player[4] = int(player[4])
                player[5] = int(player[5])
                player[6] = int(player[6])
                player[7] = int(player[7])
                ListPlayers.append(player)

                numberOne.append(player[1])
                numberOne.append(clientsocket)
                numberOne.append(addr)
                Ordem.append(numberOne)

                """for i in range(len(ListPlayers)):
                if(ListPlayers[i][0] == player[0]):
                    ListPlayers.clear()
                    ListPlayers.append(player)
                    break"""
            else:
                break


        except Exception as error:
            print("Erro na conexão com o cliente!!")
            return

"""
    Caso queira finalizar o cliente
    clientsocket.close() 


    Caso queira enviar uma resposta ao cliente
    clientsocket.send(data)
"""

def main(argv):
    try:
        # AF_INET: indica o protocolo IPv4. SOCK_STREAM: tipo de socket para TCP,
        i = 0
        global clients
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            while(i != 2):
                clientsocket, addr = server_socket.accept()
                print('Conectado ao cliente no endereço:', addr)
                clients += 1
                t = Thread(target=NewClient, args=(clientsocket,addr))
                t.start()   
                numGame = 0
                numRound = 0
                i += 1
           
        while(True):       
            play = int(input("_____ OPÇÕES DE JOGO: _____\n\n1 - Jogar\n2 - Sair\n----> "))
                
            if(play == 1 and clients >= 1):
                    
                #Cria um novo Round de Jogo
                

                #Cria um baralho com 52 cartas e embaralha as cartas
                cheap = ResetCheap()
                Round(numRound,cheap)
                numRound += 1
                    
                #Finaliza o game caso queira, ou continua
                keepPlaying = input("Deseja continuar jogando? [s/n] \n----> ")
                if(keepPlaying == "s" or keepPlaying == "S"):
                    numGame += 1
                else:
                    print('\n*********************************\n************ PLACAR ************\n*********************************\n')
                    for i in range(len(ListPlayers)):
                        print("\n", ListPlayers[i][1],"\n---------------------------------\nCidade: ",ListPlayers[i][2],"\nCarteira: R$", ListPlayers[i][3], "\nVitorias: ", ListPlayers[i][4], "\n")
                    break
                
            elif(play == 1 and clients < 1):
                print("Esperando novos jogadores entrarem !!\n---->", clients," Atualmente\n---->",(2-clients)," Faltam")
            elif(play == 2):
                print("Saindo do jogo")
                for i in range(len(ListPlayers)):
                    print("\n", ListPlayers[i][1],"\n---------------------------------\nCidade: ",ListPlayers[i][2],"\nCarteira: R$", ListPlayers[i][3], "\nVitorias: ", ListPlayers[i][4], "\n")
                break
                
            else:
                print("Opção errada !!\n")   
                

                
    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)        
        return             



if __name__ == "__main__":   
    main(sys.argv[1:])