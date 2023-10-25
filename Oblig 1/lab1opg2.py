
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
    liste = [4,4,4,4,4,4,4] #Liste med tall
    resultat = jainsall(liste) #Henter resultatet
    print(resultat) #Skriver ut resultatet

#kjører main
main()

#Resultat = 1