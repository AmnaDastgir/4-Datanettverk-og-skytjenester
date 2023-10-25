def jains(tall1, tall2):
    #res1 er øverste del JFI formelen. 
    res1 = tall1+tall2
    res1 = res1**2
    #Tall1 og tall2 plusses sammen, og svaret opphøyes i 2

    #res2 er underdelen av JFI formelen
    res2 = (tall1**2)+(tall2**2)
    res2 = res2*2
    #Tall1 og tall2 opphøyes i 2 hver for seg, derretter plusses de sammen
    #Til slutt ganges det med 2 fordi det er N.
    
    jfi = res1/res2 
    #tar svaret fra øverste del og deler det på svaret fra nederste del
    return jfi
    #returnerer svaret fra JFI.



#funksjonen main som kaller jains og skriver den ut
def main(): 
     print(jains(3,3))

#kjører main
main()

#Resultat = 1