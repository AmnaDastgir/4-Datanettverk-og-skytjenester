from queue import Empty
from socket import *
import _thread as thread
import socketserver


#lage array her som inneholder alle klienter som kobler seg tl
tilkoblet=[]


#denne lager en traad for hver connection, saa alle blir ikke inni her en funksjonen vil kjoore samtidig om flere blir sendt inn.
def handleClient(connection, addr):
    
    
    #legger til i liste
    tilkoblet.append(connection);
    #Kaller broadkast og sender inn den som er klienten som kobler til foorst. 
    hei = "En person har joina"
    broadcast(connection, hei)

   

    
    while True:
            #tar i mot meldinger fra hver klient
            data = connection.recv(1024).decode()
            
            
            if (data == "exit"):
                break
#Kaller brodcast med connection og sender inn meldingen vi mottok.
            broadcast(connection, data)
            
    connection.close() #avslutter connection
    tilkoblet.remove(connection); #Fjerner connection fra listen når den ikke er tilkoblet lenger


def broadcast(hoved, melding):
    
    
    #Hvis broadcast kkalles med en person har joinet:
    if (melding =="En person har joina"):
        #Looper gjennom alle 
        for klient in tilkoblet:
        #sjekk om det er klienten som tilkoblet foorst. hvis det ikke er det sender vi melding.
            if (klient is not hoved):
                klient.send(melding.encode());
    #hvis det er annen melding vi sender med broadcast  
    else:
        for klient in tilkoblet:
        #sjekk om det er klienten som tilkoblet foorst. hvis det ikke er det sender vi meldingen til de andre klientene.
            if (klient is not hoved):
                klient.send(melding.encode());

    

def main():
    #Setter porten-Dette er serverporten vi maa ha i klienten etterpaa.
    serverPort = 1234 
    #Oppretter TCP socket.-standardfunksjon i pyton.
    socketServer = socket(AF_INET, SOCK_STREAM)
    try:
    #linje med Python-kode som binder en socket til en spesifikk IP-adresse og port.Sender med argumenter. Med andre ord, setter opp socketen til aa lytte til alle tilgjengelige IP-adresser paa den angitte porten.
        socketServer.bind(('127.0.0.1', serverPort)) 
    except:
        print("Bind failed. Error : ")
    #Server begynner aa lytte for innkommende TCP request. argumentet angir maksimal antall tilkoblingsforespoorsler som kan vaere i koo foor nye tilkoblingsforespoorsler blir avvist. Ved aa sette denne verdien til 1, angir vi at bare en enkelt tilkoblingsforespoorsl kan vaere i koo foor de blir avvist
    socketServer.listen(1) 
    print('Server er klar til aa ta i mot ')

    #Saa lenge den er sann saa aksepter
    while True:
        #kaller metoden "accept" paa socketen og venter paa en tilkoblingsforespoorsel fra en klient. Naar en tilkobling er etablert, returnerer "accept" metoden en ny socket (kalt "client") som kan brukes til aa sende og motta data til/fra klienten, samt en tuple med informasjon om klientens IP-adresse og portnummer (kalt "addr")
        cSocket, addr = socketServer.accept() 
        print('server er tilkoblet med ' , addr)
        #oppretter ny prosess/tråd 
        thread.start_new_thread(handleClient, (cSocket,addr))

    socketServer.close()
    
    



main()  
    
 
    
