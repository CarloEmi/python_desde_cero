
def prueba(a, b):
    resultado = a + b
    print("el resultado es = ",resultado)
    return resultado

res = prueba(1,1)

if  res == 2:
    print("es igual a dos")
else:
    print("no es el nro buscado, el nro es", res)
    
'''
En esta sección se va a mostrar los append, extend, pop, etc.
'''
vocal = [ 'a', 'e ', 'i', 'o' ]
vocal.append('u')
print(vocal)

masvocal=['h', 'i', 'j']
vocal.extend (masvocal)
print(vocal)

vocal.pop(5)
print(vocal)

vocal.insert(5,'a')
print(vocal)

vocal.insert(6,'e')
print(vocal)

vocal.pop()
print(vocal)

vocal.append('o')
print(vocal)

vocal.append('u')
print(vocal)

vocal.reverse()
print(vocal)