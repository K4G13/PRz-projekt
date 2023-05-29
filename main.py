# -*- coding: utf-8 -*-
# mpiexec -n 4 python -B main.py 2 3
from mpi4py import MPI
import sys
import time
import random
import threading

# STAŁE
comm = MPI.COMM_WORLD
RANK = comm.rank  # Identyfikator procesu kradzieja
K = comm.Get_size()  # Ilość kradziejów
S = int(sys.argv[1])  # Ilość sprzętów do kradziejowania humoru :o
N = int(sys.argv[2])  # Ilość miejsc w laboratorium
EQUIPMENT_CHARGING_TIME = 5  # Czas ładowania sprzętu
CITY_CIRCULATION_TIME = (1,4)  # Czas krążenia po mieście (min,max)
GOOD_MOOD_PROBABILITY = 0.80  # Prawdopodobieństwo złapania dobrego humoru


def log(lamport_clk, msg, eq="", ack_a=""):
    colors = [
        '\033[0m',  # gray
        '\033[91m',  # red
        '\033[92m',  # green
        '\033[93m',  # yellow
        '\033[94m',  # blue
        '\033[95m',  # purple
        '\033[96m',  # cyan
        '\033[97m',  # white
        '\033[100m',  # gray background
        '\033[101m',  # red background
        '\033[102m',  # green background
        '\033[103m',  # yellow background
        '\033[104m',  # blue background
        '\033[105m',  # purple background
        '\033[106m',  # cyan background
        '\033[107m',  # white background
    ]
    print(f"{colors[RANK % len(colors)]}KRADZIEJ [{RANK:>2}]  l_c={lamport_clk:<3}  eq={eq:<3}  ack={ack_a:<3}  {msg}{colors[0]}")


def get_messages():
    messages = []
    while True:
        status = MPI.Status()
        if comm.iprobe(source=MPI.ANY_SOURCE, status=status):
            message = comm.recv(source=status.Get_source())
            messages.append((status.Get_source(), message))
        else:
            break
    return messages


def send_request(critical_section_number, lamport_clk):
    for dest_id in range(K):
        if dest_id != RANK:
            comm.send(f"REQ,{critical_section_number},{lamport_clk}", dest=dest_id)


def send_ack(critical_section_number, dest_id, lamport_clk):
    comm.send(f"ACK,{critical_section_number},{lamport_clk}", dest=dest_id)


def charge_equipment():
    print(" > SPRZET LADUJE SIE")
    time.sleep(EQUIPMENT_CHARGING_TIME)
    print(" > SPRZET NALADOWANY")
    for dest_id in range(K):
        comm.send("RELEASE,1,0", dest=dest_id)


if len(sys.argv) != 3:
    if RANK == 0:
        print("\033[91m(!) Za malo argumentow")
        print(
            "\033[93mSprobuj: mpiexec -n <ilosc_kradziejow> python -B main.py <ilosc_sprzetow> <ilosc_miejsc_w_laboratorium>\033[0m")
    exit(-1)

if int(sys.argv[1]) <= 0:
    if RANK == 0:
        print("\033[91m(!) Bledna ilosc sprzetow")
        print(
            "\033[93mSprobuj: mpiexec -n <ilosc_kradziejow> python -B main.py <ilosc_sprzetow> <ilosc_miejsc_w_laboratorium>\033[0m")
    exit(-1)

if int(sys.argv[2]) <= 0:
    if RANK == 0:
        print("\033[91m(!) Bledna ilosc miejsc w laboratorium")
        print(
            "\033[93mSprobuj: mpiexec -n <ilosc_kradziejow> python -B main.py <ilosc_sprzetow> <ilosc_miejsc_w_laboratorium>\033[0m")
    exit(-1)


if __name__ == "__main__":

    # INICJACJA ZMIENNYCH KRADZIEJA
    lamport_clk = 0  # Zegar lamporta procesu kradzieja
    cs_flag_1 = "Released"  # Flaga procesu kradzieja dla PIERWSZEJ sekcji krytycznej
    cs_flag_2 = "Released"  # Flaga procesu kradzieja dla DRUGIEJ sekcji krytycznej
    equipment_amount = S    # Aktualna pamiętana ilość dostępnych sprzętów (może być ujemna!)
    requests_queue = []     # Kolejka requestów
    ack_amount = 0          # Aktualna ilość dostanych ACK    
    log(lamport_clk, "Init", eq=equipment_amount, ack_a=ack_amount)

    while True:

        messages = get_messages()
        #OBSŁUGA WIADOMOŚCI
        for message in messages:
            author = int(message[0])
            content = message[1].split(",")
            msg_type = content[0]           # content[0]: Typ wiadomości
            cs_n = int(content[1])          # content[1]: Której sekcji dotyczy
            author_clk = int(content[2])    # content[2]: Zegar lamporta autora

            #RELEASE
            if msg_type == "RELEASE":
                equipment_amount += 1
                log(lamport_clk,f"Dostal RELEASE od [{author}]",eq=equipment_amount,ack_a=ack_amount)

            #ACK
            elif msg_type == "ACK":
                if cs_flag_1 == "Wanted" or cs_flag_2 == "Wanted":
                    ack_amount += 1
                    # lamport_clk += 1
                    log(lamport_clk,f"Dostal ACK{cs_n} od [{author}]",eq=equipment_amount,ack_a=ack_amount)
            
            #REQ
            elif msg_type == "REQ":
                if cs_n == 1:

                    #DODAJ DO KOLEJKI
                    if (cs_flag_1 == "Held") or (lamport_clk < author_clk) or (lamport_clk == author_clk and RANK < author):
                        requests_queue.append(message)

                    #ODEŚLIJ ACK
                    else:
                        comm.send(f"ACK,1,{lamport_clk}", dest=author)
                        equipment_amount -= 1
                        lamport_clk += 1
                        log(lamport_clk,f"Odsyla ACK1 do [{author}]",eq=equipment_amount,ack_a=ack_amount)

                if cs_n == 2:

                    #DODAJ DO KOLEJKI
                    if (cs_flag_2 == "Held") or (lamport_clk < author_clk) or (lamport_clk == author_clk and RANK < author):
                        requests_queue.append(message)
                        
                    #ODEŚLIJ ACK
                    else:
                        comm.send(f"ACK,2,{lamport_clk}", dest=author)
                        lamport_clk += 1
                        log(lamport_clk,f"Odsyla ACK2 do [{author}]",eq=equipment_amount,ack_a=ack_amount)
            

        if cs_flag_1 == "Released":

            send_request(1,lamport_clk)
            log(lamport_clk, "Chce wejsc do SEKCJI #01", eq=equipment_amount, ack_a=ack_amount)

            ack_amount = 0
            cs_flag_1 = "Wanted"

            continue

        if cs_flag_1 == "Wanted":
            
            if ack_amount >= K - S and equipment_amount > 0:

                lamport_clk += 1
                log(lamport_clk, "WCHODZI DO SEKCJI KRYTYCZNEJ #01", eq=equipment_amount, ack_a=ack_amount)
                
                equipment_amount -= 1
                ack_amount = 0
                cs_flag_1 = "Held"

            continue

        if cs_flag_1 == "Held" and cs_flag_2 == "Released":

            good_mood_found = False
            while not good_mood_found:
                city_circulation_time = random.randint(CITY_CIRCULATION_TIME[0], CITY_CIRCULATION_TIME[1])
                log(lamport_clk, f"Krazy po miescie {city_circulation_time} s", eq=equipment_amount, ack_a=ack_amount)
                time.sleep(city_circulation_time)
                if random.random() < GOOD_MOOD_PROBABILITY:
                    good_mood_found = True
                    log(lamport_clk, "Zlapal dobry humor!", eq=equipment_amount, ack_a=ack_amount)


            send_request(2,lamport_clk)
            log(lamport_clk, "Chce wejsc do SEKCJI #02", eq=equipment_amount, ack_a=ack_amount)

            ack_amount = 0
            cs_flag_2 = "Wanted"

            continue

        if cs_flag_1 == "Held" and cs_flag_2 == "Wanted":

            if ack_amount >= K - N:
                
                lamport_clk += 1
                log(lamport_clk, "WCHODZI DO SEKCJI KRYTYCZNEJ #02", eq=equipment_amount, ack_a=ack_amount)
                print(" > WYPRODUKOWANO GUME")
                lamport_clk += 1
                log(lamport_clk, "WYCHODZI Z SEKCJI KRYTYCZNEJ #02", eq=equipment_amount, ack_a=ack_amount)

                ack_amount = 0

                for message in requests_queue:
                    author = int(message[0])
                    content = message[1].split(",")
                    msg_type = content[0]           # content[0]: Typ wiadomości
                    cs_n = int(content[1])          # content[1]: Której sekcji dotyczy
                    author_clk = int(content[2])    # content[2]: Zegar lamporta autora

                    comm.send(f"ACK,{cs_n},{lamport_clk}", dest=author)
                    if cs_n == 1:
                        equipment_amount -= 1
                    lamport_clk = max(lamport_clk,author_clk) + 1
                    log(lamport_clk,f"Odsyla ACK{cs_n} do [{author}]",eq=equipment_amount,ack_a=ack_amount)

                requests_queue = []

                charge_thread = threading.Thread(target=charge_equipment)
                charge_thread.start()

                lamport_clk += 1
                log(lamport_clk, "WYCHODZI Z SEKCJI KRYTYCZNEJ #01", eq=equipment_amount, ack_a=ack_amount)

                cs_flag_2 = "Released"
                cs_flag_1 = "Released"

                # log(lamport_clk, "U M I E R A :O", eq=equipment_amount, ack_a=ack_amount)
                # exit()


