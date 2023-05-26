#mpiexec -n 4 python -B main.py 2 3
from mpi4py import MPI
import sys

def log(rank,lamport_clk,msg):
    colors = [
        '\033[0m',   #gray
        '\033[91m',  #red
        '\033[92m',  #green
        '\033[93m',  #yellow
        '\033[94m',  #blue
        '\033[95m',  #purple
        '\033[96m',  #cyan
        '\033[97m',  #white
        '\033[100m', #gray background
        '\033[101m', #red background
        '\033[102m', #green background
        '\033[103m', #yellow background
        '\033[104m', #blue background
        '\033[105m', #purple background
        '\033[106m', #cyan background
        '\033[107m', #white background
    ]
    print(f"{colors[rank%len(colors)]}KRADZIEJ [{rank:>2}]  l_c={lamport_clk:<3}  {msg}{colors[0]}")

def get_messages(comm):
    messages = []
    while True:
        status = MPI.Status()
        if comm.iprobe(source=MPI.ANY_SOURCE, status=status): 
            message = comm.recv(source=status.Get_source())
            messages.append((status.Get_source(), message))
        else: break
    return messages

# STAŁE
comm = MPI.COMM_WORLD
RANK = comm.rank                # Identyfikator procesu kradzieja
K = comm.Get_size()             # Ilość kradziejów
S = int(sys.argv[1])            # Ilość sprzętów do kradziejowania humoru :o
N = int(sys.argv[2])            # Ilość miejsc w laboratorium
EQUIPMENT_CHARGING_TIME = 5     # Czas ładowania sprzętu
CITY_CIRCULATION_TIME = (10,60) # Czas krążenia po mieście (min,max)
GOOD_MOOD_PROBABILITY = 0.55    # Prawdopodobieństwo złapania dobrego humoru

if __name__ == "__main__":

    if len(sys.argv) != 3:
        if RANK == 0:
            print("\033[91m(!) Za malo argumentow")
            print("\033[93mSprobuj: mpiexec -n <ilosc_kradziejow> python -B main.py <ilosc_sprzetow> <ilosc_miejsc_w_laboratorium>\033[0m")
        exit(-1)

    if int(sys.argv[1]) <= 0:        
        if RANK == 0:
            print("\033[91m(!) Bledna ilosc sprzetow")
            print("\033[93mSprobuj: mpiexec -n <ilosc_kradziejow> python -B main.py <ilosc_sprzetow> <ilosc_miejsc_w_laboratorium>\033[0m")
        exit(-1)
    
    if int(sys.argv[2]) <= 0:        
        if RANK == 0:
            print("\033[91m(!) Bledna ilosc miejsc w laboratorium")
            print("\033[93mSprobuj: mpiexec -n <ilosc_kradziejow> python -B main.py <ilosc_sprzetow> <ilosc_miejsc_w_laboratorium>\033[0m")
        exit(-1)

    # INICJACJA ZMIENNYCH KRADZIEJA
    lamport_clk = 0                 # Zegar lamporta procesu kradzieja
    cs_flag_1 = "Init"              # Flaga procesu kradzieja dla PIERWSZEJ sekcji krytycznej
    cs_flag_2 = "Init"              # Flaga procesu kradzieja dla DRUGIEJ sekcji krytycznej
    equipment_amount = S            # Aktualna pamiętana ilość dostępnych sprzętów (może być ujemna!)
    requests_queue = []             # Kolejka requestów
    log(RANK,lamport_clk,"Init")

    while True:

        #ROZESŁANIE REQUESTÓW DO WSZYSTKICH ODNOŚNIE SEKCJI #1
        if cs_flag_1 == "Init" or cs_flag_1 == "Released":
            log(RANK,lamport_clk,"Zmiana flagi #1 na WANTED")
            cs_flag_1 = "Wanted"
            log(RANK,lamport_clk,f"Wysyla REQ,1,{lamport_clk} do wszystkich")
            for dest_id in range(N):
                if dest_id != RANK: 
                    comm.send(f"REQ,1,{lamport_clk}", dest=dest_id)
            continue
        
        #ODBIERA I WYSYŁA WIADOMOŚCI
        if cs_flag_1 == "Wanted":
            log(RANK,lamport_clk,"Umiera")
            exit()    


