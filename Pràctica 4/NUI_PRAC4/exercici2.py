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
        
        # inicialitzem les mitjes a zero float i una variable booleana que 
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
        
        # Per a comprovar si s'ha acabat el bucle adequadament o s'ha trencat de forma abruta
        # comprovem la variable leap. Si hem sortit abans d'hora, caldra assignar la nova
        # finestra de dades.
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
    temp_badget,invested_money,non_strategy= estrategiaBasica(broker,data[item])
    # Mostrem els resultats per pantalla
    print_results(data[item],temp_badget,invested_money,non_strategy)