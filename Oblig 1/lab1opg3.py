def jainsall(liste):
    #res1 vil være øverste del av formelen, det over streken
    res1=0
    for tall in liste:
        res1+= tall
        #legger alle tall inn i summen res1
    res1=res1**2
    #opphøyer summen i 2

    #res2 vil være nederste del av formelen
    res2 = 0
    for tall in liste:
        res2+= tall**2
        #legger alle tall opphøyd i 2 inn i summes res2
    res2=res2*len(liste)
    #ganger summen med antall elementer i listen

    jfi = res1/res2 #Utfører formelen
    return jfi #returnerer resultatet

def main():
    file = open("tre.txt","r").readlines() #henter ut hver linje fra txt filen.
    liste = [] #lager en tom liste
    for i in file:
        #Split henter ut det som er på plass 0 på den linjen
        tall = int(i.split()[0]) #parser det til tall, fordi det vi henter ut er string
        liste.append(tall) #Legger inn tallet i listen
    
    resultat = jainsall(liste) #Kaller metoden for å regne JFI
    print(resultat) 

main()

#Resultat = 0.7552011095700416