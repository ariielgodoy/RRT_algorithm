import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import LineString, Polygon

PuntoObjetivo = np.array([19, 19])
q_inicial = np.array([[10, 10, 0]])
q_new = []
epsilon = 0.5 #Este es el paso que se puede dar
Arbol = q_inicial.copy()

obstaculos = [
    (1, 1, 3, 3),
    (5, 2, 6, 5),
    (15, 15, 12, 9)
]

def Configuracion_aleatoria():
    return np.random.randint(0, 21, size=(1,2)) #genera un array 1x2 de numeros aleatorios entre 0 y 10, que es la distancia maxima en mi mapa

def VecinoMasProximo(q_rand, Arbol):
    #aqui tendria que recorrer todos los puntos para ver cual es el mas cercano a q_rand por la distancia euclidea
    mas_cerca = np.inf
    for vertice in Arbol:
        distancia = np.sqrt((vertice[0]-q_rand[0])**2 + (vertice[1]-q_rand[1])**2)
        if distancia<mas_cerca:
            mas_cerca = distancia
            vertice_mas_cercano = vertice
    
    return vertice_mas_cercano, mas_cerca



def GenerarPunto(q_near, q_rand):
    vector = q_rand[:2] - q_near[:2]
    distancia = np.linalg.norm(vector)
    if distancia == 0:
        return q_near.copy()
    q_new = np.zeros(3)
    q_new[:2] = q_near[:2] + epsilon * vector / distancia
    q_new[2] = q_near[2] + 1
    return q_new


def NuevaConfig(q_rand, q_near, q_new):
    #pendiente = (q_new[2]-q_near[2])/(q_new[1]-q_near[1])      Pongo esto para probar una primera vez
    #Para comprobar esto solo habria que ver si un punto de los obstaculos esta dentro del dominio de la funcion que forma q_near y q_new
    if q_new[0] > 20 or q_new[1] > 20:
        return False
    
    segmento = LineString([q_near, q_new])      #He decidido hacer esto asi porque en la vida real la intersección me la dará un sensor
    for (x_min, y_min, x_max, y_max) in obstaculos:
        pol = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
        if pol.intersects(segmento):
            return False
    
    return True

def AnadeVertice(q_new):
    global Arbol
    Arbol = np.vstack((Arbol, q_new))



def Extiende(q_rand):
    global Arbol
    q_near, distancia_punto = VecinoMasProximo(q_rand, Arbol)
    #que es la distancia euclidea al punto random
    q_new = np.zeros(3)
    q_new = GenerarPunto(q_near, q_rand)
    if NuevaConfig(q_rand, q_near, q_new) and distancia_punto > epsilon:
        AnadeVertice(q_new)
        plt.plot([q_near[0], q_new[0]], [q_near[1], q_new[1]], 'g-', linewidth=2)
    
    if distancia_punto < epsilon:
        return "alcanzado"
    else:
        return "avanzado"

def FormarArbol():
    global Arbol
    indice = 0
    p_mas_cercano = np.zeros(3)
    p_mas_cercano = VecinoMasProximo(PuntoObjetivo, Arbol)
    siguiente_punto = p_mas_cercano[0][2]
    print("nigga",siguiente_punto)
    mejorArbol = np.array([p_mas_cercano[0]])
    posicion = 0
    for i in Arbol:
        indice += 1
        if np.array_equal(p_mas_cercano[0][:2], i[:2]):
            posicion = indice
            break
    
    punto = p_mas_cercano[0][:2]
    while siguiente_punto > 0:
        for iterador in range(posicion):
            if (np.linalg.norm(Arbol[iterador,:2] - punto) <= epsilon + 0.1) and Arbol[iterador,2] == siguiente_punto-1:
                mejorArbol = np.vstack((mejorArbol, Arbol[iterador]))
                punto = Arbol[iterador][:2]
                siguiente_punto -= 1
                break
    
    return mejorArbol


    
    

#-----------MAIN LOOP----------#

iteraciones_maximas = 900

iteracion = 1
plt.figure(figsize=(6,6))
ax = plt.gca()

# Dibuja los obstáculos
for (x_min, y_min, x_max, y_max) in obstaculos:
    width = x_max - x_min
    height = y_max - y_min
    rect = patches.Rectangle((x_min, y_min), width, height, linewidth=1, edgecolor='r', facecolor='gray')
    ax.add_patch(rect)


for iteracion in range(iteraciones_maximas):
    q_rand = Configuracion_aleatoria()
    Extiende(q_rand[0])




mejorArbol = FormarArbol()

print(mejorArbol)
print("SEPARACION")
print(Arbol)


plt.scatter(Arbol[:,0], Arbol[:,1], c='blue', label='Nodos del árbol')
plt.scatter(mejorArbol[:,0], mejorArbol[:,1], c='red', label='Arbol más cercano')
plt.scatter(q_inicial[0,0], q_inicial[0,1], c='red', label='Nodo inicial')

plt.scatter(PuntoObjetivo[0], PuntoObjetivo[1], c='green', label='Destino')

plt.xlim(0, 20)
plt.ylim(0, 20)
plt.title("Muestreador RRT")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.legend()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()