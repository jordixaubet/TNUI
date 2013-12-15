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

        
#Testing de la funció
method1 = SlidWin(8)
v = [0.22, 0.88, 0.21, 0.41, 0.33, 0.41, 0.12, 0.43, 0.38, 0.22]

for i in range(len(v)):
    mitja, accio = method1.add(v[i])
    print "He afegit", v[i],"a la finestra a la iteració", i+1, "i m'ha retornat:"
    print " una mitja de", mitja, "i l'accio", accio
    print

# PROVA AMB DADES SINTETIQUES

# Sliding window amb un tamany de finestra ==10
method1 = SlidWin(10)
# Sliding window amb un tamany de finestra ==50
method2 = SlidWin(50)

v=[] # Genera un mostra de 400 + 600 valors amb un canvi brusc entre 400 i 401.
for i in xrange(100):
    v.append(0.6+0.1*(random.random()-0.5))
for i in xrange(200):
    v.append(0.4+0.1*(random.random()-0.5))
   
# Anem afegint de forma seqüencial les dades dins la nostra finestra lliscant. Guardem el resultat dins la llista output1 i output2
output1=[]
output2=[]
for item in v:
    mean,action=method1.add(item)
    output1.append(mean)
    mean,action=method2.add(item)
    output2.append(mean)
    
  
# Visualitzem el resultat
pylab.plot(v)
pylab.plot(output1,'r') # plot del resultat del Mètode 1
pylab.plot(output2,'g') # plot del resultat del Mètode 2
pylab.show()

# Prova amb dades de la Borsa utilizant l'estratègia bàsica que us donem
method = SlidWin(10)
for item in data:
    # Creem un objecte broker. Aquest objecte cada cop que entrem una nova dada dira si hem de comprar o vendre accions
    # per_change indica el percentatge de canvi respecte al valor de l'accio per realitzar una compra/venta
    # min_time indica el temps minim que ens hem d'esperar per fer nova accio de compra/venta
    per_change=0.1
    min_time=10
    broker= StockMarketWin(method,per_change,min_time)
    # Executem l'estrtegia de comprar a partir de l'objecte broker i les dades d'entrada. La funció estrategiaBasica 
    # està definidia dins utilsP4.py. Ella és la responsable de decidir la quantatit de compra o venta d'accios a partir de la
    # suggeriencia del broker
    temp_badget,invested_money,non_strategy= estrategiaBasica(broker,data[item])
    # Mostrem els resultats per pantalla
    print_results(data[item],temp_badget,invested_money,non_strategy)
