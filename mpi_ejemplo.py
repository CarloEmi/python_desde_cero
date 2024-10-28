from mpi4py import MPI

# Inicialización del entorno MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Enviar y recibir mensajes entre procesos
if rank == 0:
    # El proceso con rank 0 envía mensajes
    data = "Mensaje desde el proceso 0"
    comm.send(data, dest=1, tag=11)
    print(f"Proceso 0 envió: {data}")
elif rank == 1:
    # El proceso con rank 1 recibe el mensaje
    data = comm.recv(source=0, tag=11)
    print(f"Proceso 1 recibió: {data}")
else:
    print(f"Proceso {rank} no tiene nada que hacer")