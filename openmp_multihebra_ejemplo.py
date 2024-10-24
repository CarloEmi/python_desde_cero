"""
Paso a paso:
Instalar Python: Verifica que tienes Python instalado, puedes descargarlo desde python.org.
Guardar el archivo: Guarda este código como openmp_sim.py.
Ejecutar el código:
En tu terminal, navega a la carpeta donde guardaste el archivo.
Ejecuta el código con python openmp_sim.py.
Resultado esperado: Verás mensajes como "Durmiendo X segundos" y al final, el tiempo total que tomó la ejecución. Este ejemplo demuestra cómo las tareas se ejecutan en paralelo utilizando varias hebras.
Qué tener en cuenta:
La biblioteca concurrent.futures facilita el manejo de hebras sin tener que gestionar los detalles de sincronización manualmente.
En Python, el paralelismo real se limita por el Global Interpreter Lock (GIL), pero para operaciones de I/O como en este ejemplo, sigue siendo útil.
"""


import concurrent.futures
import time
# Función que realiza un cálculo (simulación de trabajo pesado)
def trabajo_pesado(segundos):
    print(f"Durmiendo {segundos} segundos...")
    time.sleep(segundos)
    return f"Terminado después de {segundos} segundos."
# Ejecutar en varias hebras
if __name__ == "__main__":
    start = time.perf_counter()
    # Creamos un executor para manejar 2 hebras simultáneas
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Ejecutar la función en paralelo con diferentes tiempos de espera
        resultados = [executor.submit(trabajo_pesado, segundos) for segundos in [5, 3, 1]]
        # Imprimir resultados una vez que estén completos
        for resultado in concurrent.futures.as_completed(resultados):
            print(resultado.result())
    finish = time.perf_counter()
    print(f"Terminado en {round(finish - start, 2)} segundos")