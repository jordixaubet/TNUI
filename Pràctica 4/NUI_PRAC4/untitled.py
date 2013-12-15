# coding: utf-8
# Comanda d'execució: ipython notebook NUI_prac4.ipynb --pylab inline

from utilsP4 import *
# %matplotlib inline 

# Carreguem les dades de la borsa mitjaçant la funció loadStockData
data={}
#companies=['GOOG','MSFT','IBM','YHOO','FB']
companies=['GOOG']
for c in companies:
    data[c]=loadStockData(c)
"""


EXERCICI 1


"""
class SlidWin:
    """
        Finestra lliscant que permet trobar la mitja d'una sèrie de dades de mida màxima W_size.
        Aquesta finestra lliscant recalcula la mitja amb les fòrmules d'increment i decrement que es troben més abaix d'aquest fitxer.
    """
    def __init__(self, W_size):
        """
            Constructor que inicialitza els paràmetres per la finestra lliscant.
            param W_size Mida màxima de la finestra lliscant.
        """
        self.data = [] # dades
        self.W_size = W_size # tamany de la finestra
        self.length = 0 # length actual de la finestra
        self.m = 0.0 # mitja de la finestra
    def add(self, x_t):
        """
            Afegeix una nova dada a la finestra i retorna la mitja d'aquesta i el valor de l'accio:.
            return 	new_mean,  1  : si la mitja ha disminuït
					new_mean, -1  : si la mitja ha augmentat
                    new_mean,  0  : si la mitja es identica
        """
        #Les primeres dades que encara no son de l'amplada de la finestra s'afegeixen de cop
        #i incrementen el valor del self.length
        if self.length < self.W_size:
            self.data.append(x_t)
            self.length += 1
        #A partir de que tenim la finestra "plena", cada vegada que entra una dada desplaçem les
        #que ja hi ha, eliminant-ne la mes vella i afegint-hi la mes nova
        else:
            for i in range(self.W_size-1):
                self.data[i] = self.data[i+1]
            self.data[self.length-1] = x_t
        
        #Calculem la mitja del vector
        new_mean = 0
        for i in range(self.length):
            new_mean += self.data[i]
        new_mean /= self.length
        
        old_mean = self.m
        #Assignem la nova mitja al valor de mitja de la classe
        self.m = new_mean
        
        if new_mean < old_mean:
            return new_mean, 1
        elif new_mean > old_mean:
            return new_mean, -1
        else:
            return new_mean, 0

        
# #Testing de la funció
# method1 = SlidWin(8)
# v = [0.22, 0.88, 0.21, 0.41, 0.33, 0.41, 0.12, 0.43, 0.38, 0.22]

# for i in range(len(v)):
#     mitja, accio = method1.add(v[i])
#     print "He afegit", v[i],"a la finestra a la iteració", i+1, "i m'ha retornat:"
#     print " una mitja de", mitja, "i l'accio", accio
#     print

# # PROVA AMB DADES SINTETIQUES

# # Sliding window amb un tamany de finestra ==10
# method1 = SlidWin(10)
# # Sliding window amb un tamany de finestra ==50
# method2 = SlidWin(50)

# v=[] # Genera un mostra de 400 + 600 valors amb un canvi brusc entre 400 i 401.
# for i in xrange(100):
#     v.append(0.6+0.1*(random.random()-0.5))
# for i in xrange(200):
#     v.append(0.4+0.1*(random.random()-0.5))
   
# # Anem afegint de forma seqüencial les dades dins la nostra finestra lliscant. Guardem el resultat dins la llista output1 i output2
# output1=[]
# output2=[]
# for item in v:
#     mean,action=method1.add(item)
#     output1.append(mean)
#     mean,action=method2.add(item)
#     output2.append(mean)
    
  
# # Visualitzem el resultat
# pylab.plot(v)
# pylab.plot(output1,'r') # plot del resultat del Mètode 1
# pylab.plot(output2,'g') # plot del resultat del Mètode 2
# pylab.show()

# # Prova amb dades de la Borsa utilizant l'estratègia bàsica que us donem
# method = SlidWin(10)
# for item in data:
#     # Creem un objecte broker. Aquest objecte cada cop que entrem una nova dada dira si hem de comprar o vendre accions
#     # per_change indica el percentatge de canvi respecte al valor de l'accio per realitzar una compra/venta
#     # min_time indica el temps minim que ens hem d'esperar per fer nova accio de compra/venta
#     per_change=0.1
#     min_time=10
#     broker= StockMarketWin(method,per_change,min_time)
#     # Executem l'estrtegia de comprar a partir de l'objecte broker i les dades d'entrada. La funció estrategiaBasica 
#     # està definidia dins utilsP4.py. Ella és la responsable de decidir la quantatit de compra o venta d'accios a partir de la
#     # suggeriencia del broker
#     temp_badget,invested_money,non_strategy= estrategiaBasica(broker,data[item])
#     # Mostrem els resultats per pantalla
#     print_results(data[item],temp_badget,invested_money,non_strategy)


"""


EXERCICI 2


"""

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

# # PROVA AMB DADES SINTETIQUES

# # Adatptative window amb d=0.98
# method1 = AdWin(0.95)

# v=[] # Genera un mostra de 400 + 600 valors amb un canvi brusc entre 400 i 401.
# for i in xrange(200):
#     v.append(0.6+0.1*(random.random()-0.5))
# for i in xrange(400):
#     v.append(0.4+0.1*(random.random()-0.5))
# for i in xrange(600):
#     v.append(0.1*(random.random()-0.5))
    
# # Anem afegint de forma seqüencial les dades dins la nostra finestra lliscant. Guardem el resultat dins la llista output1 i output2
# output1=[]
# for item in v:
#     mean,action=method1.add(item)
#     output1.append(mean)
    
  
# # Visualitzem el resultat
# pylab.plot(v)
# pylab.plot(output1,'r') # plot del resultat del Mètode 1
# pylab.show()

# # Prova amb dades de la Borsa utilizant l'estratègia bàsica que us donem
# method = AdWin(0.95)
# for item in data:
#     # Creem un objecte broker. Aquest objecte cada cop que entrem una nova dada dira si hem de comprar o vendre accions
#     # per_change indica el percentatge de canvi respecte al valor de l'accio per realitzar una compra/venta
#     # min_time indica el temps minim que ens hem d'esperar per fer nova accio de compra/venta
#     broker= StockMarketWin(method,0.1,10)
#     # Executem l'estrtegia de comprar a partir de l'objecte broker i les dades d'entrada. La funció estrategiaBasica 
#     # està definidia dins utilsP4.py. Ella és la responsable de decidir la quantatit de compra o venta d'accios a partir de la
#     # suggeriencia del broker
#     temp_badget,invested_money,non_strategy= estrategiaBasica(broker,data[item])
#     # Mostrem els resultats per pantalla
#     print_results(data[item],temp_badget,invested_money,non_strategy)

"""

EXERCICI 3

"""
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
    
    accio_prev = -1;
    prev_value = 0;

    rati_compra = 0.8
    rati_venda = 0.2
    
    cont=0;
    # iterem les dades de forma seqüencial simulant una partida de joc
    for current_value in data:
        # afegim una nova dada i obtenim l'accio recomanada pel broker
        action  = broker.add(float(current_value))

        # diferencia = math.fabs(float(current_value) - prev_value);
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
        prev_value = float(current_value)
    return temp_badget,invested_money,non_strategy

# PROVA AMB DADES SINTETIQUES

# Adatptative window amb d=0.98
method1 = AdWin(0.95)

v=[] # Genera un mostra de 400 + 600 valors amb un canvi brusc entre 400 i 401.
for i in xrange(200):
    v.append(0.6+0.1*(random.random()-0.5))
for i in xrange(400):
    v.append(0.4+0.1*(random.random()-0.5))
for i in xrange(600):
    v.append(0.1*(random.random()-0.5))
    
# Anem afegint de forma seqüencial les dades dins la nostra finestra lliscant. Guardem el resultat dins la llista output1 i output2
output1=[]
for item in v:
    mean,action=method1.add(item)
    output1.append(mean)


# Visualitzem el resultat
pylab.plot(v)
pylab.plot(output1,'r') # plot del resultat del Mètode 1
pylab.show()

# Prova amb dades de la Borsa utilizant l'estratègia bàsica que us donem
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