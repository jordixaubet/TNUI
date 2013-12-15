# coding: utf-8
"""
	
	Per a aquest exercici hem tingut en compte l'accio actual, recomanada per StockMarketWin
	i l'accio anterior recomanada. Si ens recomana dues vegades segudes la mateixa acció
	voldra dir que el mercat, en aquell moment, tindra una tendencia a l'alça o la baixa.
	Mentre es mantingui la tendencia conprarem, o vendrem, pero cada vegada que es porti a
	terme una de les dues accions la quantitat de diners gastats o d'accions venudes es
	modificara, per a poder millorar la rendibilitat.

"""

from utilsP4 import *
# %matplotlib inline 

# Carreguem les dades de la borsa mitjaçant la funció loadStockData
data={}
#companies=['GOOG','MSFT','IBM','YHOO','FB']
companies=['GOOG']
for c in companies:
    data[c]=loadStockData(c)

def estrategia(broker,data,budget=100000.00):
    """
        Definim una estrategia de joc. 
        Parametres d'entrada : StockMarketWin 
                             : Dades - dades que utilizarem per fer el test
                             : budget- quantitat de diners que volem jugar
    """
    # Definim els parametres inicials de l'estrategia
    # Gastem el 50% del budget en accions
    n_stocks= math.floor((budget/2)/float(data[0]))
    init_stocks=n_stocks
    # Descomptem del budget el valor de les acciones que hem comprat
    budget = budget - n_stocks * float(data[0])
    
    # inicialitzem variables
    invested_money=np.zeros(len(data))
    temp_badget=np.zeros(len(data))
    non_strategy=np.zeros(len(data))

	# Creem tres variables que usarem per gestionar la compra-venda d'accions
	# La primera ens servira per comprarar l'accio actual amb l'anterior, donada per StockMarketWin
    accio_prev = 0;
    # Les altres dues seran per graduar els ratis de compra i venda, que anirem graduant de forma dinamica
    rati_compra = 0.8
    rati_venda = 0.2
    
    cont=0;
    # iterem les dades de forma seqüencial simulant una partida de joc
    for current_value in data:
        # afegim una nova dada i obtenim l'accio recomanada pel broker
        action  = broker.add(float(current_value))

        # Si ens surt dues vegades seguides o mes la mateixa accio,
        # executem el que toqui fer en aquell moment
        if action != None:
            if action[1] == accio_prev:
                if action[1] == -1: # ACCIÓ COMPRA
                    # Com que comprem, reiniciem el rati de vendes
                    rati_venda = 0.2

                    money2spend=rati_compra*budget
                    new_actions = math.floor(money2spend/float(current_value))
                    n_stocks+= new_actions
                    budget-=new_actions*float(current_value)

                    # Determino un límit de 0.2 com a mínim de rati de vendes
                    if rati_compra > 0.2:
                        #El reduim cada vegada mes, ja que cada cop son mes cares les accions
                        rati_compra -= 0.01

                if action[1] == 1: # ACCIÓ VENTA
                    # Com que venem, reiniciem el rati de compres
                    rati_compra = 0.8

                    actions2sell=round(rati_venda*n_stocks)
                    n_stocks-= actions2sell
                    budget+=actions2sell*float(current_value)

                    if rati_venda < 0.8:
                        # Augmentem el rati cada vegada mes, ja que cada cop surt menys a compte vendre, en podem treure menys rendibilitat
                        rati_venda += 0.01

        temp_badget[cont]=budget
        invested_money[cont]=n_stocks*float(current_value)
        non_strategy[cont]=(budget/2) + init_stocks*float(current_value)
        cont=cont+1

        # Nomes volem considerar com a accio previa la última accio de commpra-venda realitzada
        if action[1] != 0:
            accio_prev = action[1];
    return temp_badget,invested_money,non_strategy

class AdWin:
    """
        Finestra lliscant adaptativa que permet trobar la mitja de totes les dades que es van inserin i que permet trobar canvis bruscos
        en elles i adaptar-se a ells a partir d'un valor de confiança indicat per l'usuari.
    """
    def __init__(self, d):
        """
            Constructor de la finestra.
            
            param d Confiança el canvi. Com més gran més fàcil serà detectar un canvi.
        """
        self.data = []
        self.length = 0
        self.rel = d
        self.m = 0.0
        
    def add(self, x_t):
        
        # Desem la mitja anterior per a poder fer la comparacio d'opcions al final del proces
        mprev = self.m

        # Afegim la nova dada a la llista i incrementem la mida
        self.data.append(x_t)
        self.length += 1

        # Si els la única dada que tenim, la mitja es la propia dada i retornem 1 al valor d'opció ja que es mes gran
        # la mitja actual que la previa
        if self.length == 1:
            self.m = x_t
            return x_t, 1
        
        # inicialitzem les mitjes a zero float i una variable booleana que posarem
        # modificarem en cas de que sortim prematurament del bucle for
        m0 = 0.0
        m1 = 0.0
        leap = False
        
        # Recorrem la llista a cada addició creant-ne subgrups
        for i in range(self.length):
            w0 = self.data[:i]
            w1 = self.data[i:]

            if len(w0) != 0 and len(w1) != 0:

                m0 = float(sum(w0)/len(w0))
                m1 = float(sum(w1)/len(w1))

                val = self.ecut(len(w0), len(w1))
                if math.fabs(m0 - m1) > val:
                    leap = True
                    break
            
        if leap:
            self.data = w1
            self.length = len(w1)

        self.m = sum(self.data) / self.length
        
        if (self.m - mprev) > 0:
            compra = 1
        elif (self.m - mprev) == 0:
            compra = 0
        else:
            compra = -1
            
        return self.m, compra

    def ecut(self, n1, n2):
        m = 1.0/( (1.0/n1) + (1.0/n2))
        delta = self.rel / (n1+n2)
        aux = ( 1.0 / (2 * m) ) * math.log( 4.0 / delta )
        return math.sqrt(aux)

method = AdWin(0.95)
for item in data:
    # Creem un objecte broker. Aquest objecte cada cop que entrem una nova dada dira si hem de comprar o vendre accions
    # per_change indica el percentatge de canvi respecte al valor de l'accio per realitzar una compra/venta
    # min_time indica el temps minim que ens hem d'esperar per fer nova accio de compra/venta
    broker= StockMarketWin(method,0.1,10)
    # Executem l'estrtegia de comprar a partir de l'objecte broker i les dades d'entrada. La funció estrategiaBasica 
    # està definidia dins utilsP4.py. Ella és la responsable de decidir la quantatit de compra o venta d'accios a partir de la
    # suggeriencia del broker
    temp_badget,invested_money,non_strategy= estrategia(broker,data[item])
    # Mostrem els resultats per pantalla
    print_results(data[item],temp_badget,invested_money,non_strategy)