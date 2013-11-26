# -*- coding: utf-8 -*-
import pylab
import ystockquote
import numpy as np
import math
import random


# Carreguem les dades reals de la borsa 
def loadStockData(company):
    data = ystockquote.get_historical_prices(company,'1990101','20131120')
    # Creem una llista amb els valors del tancament diari de la borsa
    values = [ data[i][6] for i in range(1, len(data))]
    values.reverse()
    # Mostrem la gràfica amb el preu de l'acció
    pylab.plot(values)
    pylab.title(company)
    pylab.ylabel(r"Preu accio ($USD)", fontsize = 12)
    pylab.xlabel(r"Data index", fontsize = 12)
    pylab.grid(True)
    pylab.show()
    return values  

"""
    StockMarketWin és un gestor de borsa que ens indicara si hem de comprar o vendre accions. 
    S'ha d'especificiar quin mètode d'analisi de dades temporals utilizarà : {SlidWin, AdWin}
""" 
class StockMarketWin:
    def __init__(self, method, percentatge, adapt_time):
        """
            Constructor del StockMarketWin per la compra i venta d'accions a la borsa.
            
            method: Objecte de la classe que utilizarem per a l'analisi de les dades (SlidWin, AdWin)
            
            param percentatge Percentatge sobre les dades obtingudes fins a un instant de temps sobre el que calcularem el 
            max i el min. Com més petit sigui més fàcil serà detectar canvis (ha de ser un valor entre 0 i 1).
            Si l'escenari en el que treballem és brusc podem posar un percentatge major.
            Si és suau podem posar un percentatge menor.
            
            param adapt_time Enter que indica el nombre de valors que han d'entrar per reconsiderar una modificació de 'm_lastAction'.
            """
        # mètode de la finestre
        self.method= method
        #Guarda la última acció feta i la mitja en aquell punt per saber que la pròxima vegada hauriem de fer el contrari
        # i obtenint un benefici segons la mitja de m_lastAction
        self.lastAction = "COMPRA"
        self.m_lastAction = 0
        # Temps necessari per recalcular la adaptació de les dades en el cas de que haguem de modificar m_lastAction 
        #fins i tot si no hi ha beneficis
        # Per exemple: quan la borsa no para de baixar i baixen les probabilitats de que superi el valor establert anteriorment
        self.adapt_time = adapt_time
        self.time = 0
        # Min i Max per normalitzar
        self.max = 0
        self.min = 0
        # Percentatge sobre el qual trobem el min i el max
        self.percentatge = percentatge
        
    def add(self, x_t):
        """
			Afegeix una dada a la finestra i fa les comprovacions necessàries per saber si ha de comprar o ha de vendre
			i per recalcular els atributs de la classe que li permeten distingir canvis interessants per la compra-venta.
            return: nova mitja i accio suggerida: (1 Compra, -1 Venta)
		"""
		# Calculem el max i el min inicials
        if(self.method.data == []):
			self.m_lastAction = x_t
			self.max = x_t + x_t*self.percentatge
			self.min = x_t - x_t*self.percentatge
        self.time += 1
        # Inserim les dades a la finestra normalitzan't-les a partir del min i max establerts
        new_m, compra = self.method.add(self.__getNormalized(x_t))
        new_m = self.__getOriginal(new_m)
        
        # Si hi ha hagut un canvi a les dades:
        if(compra != 0):
            
            # Recuperem les dades i les normalitzem sobre els nous màxims i mínims
            aux = []
            for d in self.method.data:
                aux.append(self.__getOriginal(d))
            self.max = new_m + new_m*self.percentatge
            self.min = new_m - new_m*self.percentatge
            aux2 = []
            for d in aux:
                aux2.append(self.__getNormalized(d))
            self.method.data = aux2
            self.method.m = self.__getNormalized(new_m)
            
            # Comprem o venem si les mitjes actuals són més favorables que les que hi
            # havia en aquell moment i si l'acció anterior era contrària.
            if((compra == 1) and (self.lastAction == "VENTA") and (self.m_lastAction > new_m)):
                self.lastAction = "COMPRA"
                self.m_lastAction = new_m
                self.time = 0
                return new_m,1
            elif((compra == -1) and (self.lastAction == "COMPRA") and (self.m_lastAction < new_m)):
                self.lastAction = "VENTA"      
                self.m_lastAction = new_m
                self.time = 0
                return new_m, -1
			# Si els valors segueixent baixant durant un període de temps llarg fins i tot després d'haver 
            # comprat actualizem la mitja
            elif((compra == 1) and (self.lastAction == "COMPRA") and (self.time > self.adapt_time)):
                self.m_lastAction = new_m
                self.time = 0
                return new_m, 1
            # Si passa el mateix que en el cas anterior però pujant i després d'haver venut també actualizem
            elif((compra == -1) and (self.lastAction == "VENTA") and (self.time > self.adapt_time)):
                self.m_lastAction = new_m
                self.time = 0
                return new_m, -1
            return new_m, 0
        
    def __getNormalized(self, x_t):
		"""
			Normalitza la dada introduïda a partir del màxim i el mínim establerts.
		"""
		if(self.max-self.min)==0:
			return x_t - self.min
		return (x_t - self.min)/(self.max-self.min)
    def __getOriginal(self, x_t_norm):
		"""
			Retorna la dada original a partir de la normalitzada recalculant amb el màxim i el mínim.
		"""
		return (self.max - self.min) * x_t_norm + self.min

'''
	Imprimeix el resultats obtinguts per pantalla
'''
def print_results(data,temp_badget,invested_money,non_strategy):
    print "******************************************************************"
    print "*  "
    print "*  ---------Valor inicial de la acció ", data[0], "  -------------"
    print "*  ----------------------------------------------------------"
    print "*  INICI: Diners  = ", temp_badget[0] + invested_money[0]
    print "*  INICI: Valor accions = ", invested_money[0],  " ( #accions =", invested_money[0]/float(data[0]), "*Valor Accions=", data[0], ")"
    print "*  INICI: Diners sense invertir = ", temp_badget[0]  
    print "*  ----------------------------------------------------------"
    print "*  ----------------------------------------------------------"
    print "*  ----------------------------------------------------------"
    print "*  FINAL: Diners  = ", temp_badget[-1] + invested_money[-1]
    print "*  FINAL: Valor accions = ", invested_money[-1],  " ( #accions =", invested_money[-1]/float(data[-1]), "*Valor Accions=", data[-1], ")"
    print "*  FINAL: Diners sense invertir = ", temp_badget[-1]  
    print "*  ----------------------------------------------------------"
    print "*  ----------------------------------------------------------"
    print "*  Benefici Global= ", temp_badget[-1] + invested_money[-1] - 100000.0 
    print "*  Benefici produit pel Broker = ",  temp_badget[-1] + invested_money[-1] - (50000  + math.floor(50000/float(data[0])) *float(data[len(data)-1]))
    print "*  ----------------------------------------------------------"
    print "******************************************************************"


    pylab.subplot(2,1, 1),pylab.plot(data),pylab.title("Valor de les Accions")
    pylab.ylabel(r" Valor Accio ($USD)", fontsize = 12),
    pylab.xlabel(r"Date Index", fontsize = 12),
    pylab.grid(True)
    
    pylab.subplot(2,1, 2),
    pylab.plot(invested_money+temp_badget,'g')
    pylab.plot(temp_badget),
    pylab.plot(invested_money,'c'),
    pylab.plot(non_strategy,'r')
    
    pylab.legend(["$ total ","$ sense invertir","$ invertits","$ sense Estrategia",],bbox_to_anchor=(1.05, 1),loc=2,borderaxespad=0.)
    pylab.title(""),
    pylab.ylabel(r"($USD)", fontsize = 12),
    pylab.xlabel(r"Date", fontsize = 12),
    pylab.grid(True)

    pylab.show()   


'''
	Estrategia basica de joc
'''
def estrategiaBasica(broker,data,badget=100000.00):
    """
        Definim una estrategia de joc. 
        Parametres d'entrada : StockMarketWin 
                             : Dades - dades que utilizarem per fer el test
                             : badget- quantitat de diners que volem jugar
    """
    # Definim els parametres inicials de l'estrategia
    # Gastem el 50% del badget en accions
    n_stocks= math.floor((badget/2)/float(data[0]))
    init_stocks=n_stocks
    # Descomptem del badget el valor de les acciones que hem comprat
    badget = badget - n_stocks * float(data[0])
    
    # inicialitzem variables
    invested_money=np.zeros(len(data))
    temp_badget=np.zeros(len(data))
    non_strategy=np.zeros(len(data))
    
    cont=0;     
    # iterem les dades de forma seqüencial simulant una partida de joc
    for current_value in data:
        # afegim una nova dada i obtenim l'accio recomanada pel broker
        action  = broker.add(float(current_value))
        if action != None:
            if action[1] == -1: # ACCIÓ COMPRA
                #Gastem el 25% del badget que tenim"
                money2spend=0.25*badget
                new_actions = math.floor(money2spend/float(current_value))
                n_stocks+= new_actions
                badget-=new_actions*float(current_value)
            if action[1] == +1: # ACCIÓ VENTA
                #Venem el 25% de les accions que tenim"
                actions2sell=round(0.25*n_stocks)
                n_stocks-= actions2sell
                badget+=actions2sell*float(current_value)
        temp_badget[cont]=badget
        invested_money[cont]=n_stocks*float(current_value)
        non_strategy[cont]=(badget/2) + init_stocks*float(current_value)
        cont=cont+1
    return temp_badget,invested_money,non_strategy
    
