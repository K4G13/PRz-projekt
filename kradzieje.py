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
EQUIPMENT_CHARGING_TIME = 10  # Czas ładowania sprzętu
CITY_CIRCULATION_TIME = (5, 15)  # Czas krążenia po mieście (min,max)
GOOD_MOOD_PROBABILITY = 0.70  # Prawdopodobieństwo złapania dobrego humoru


def log(lamport_clk, msg):
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
    print(f"{colors[RANK % len(colors)]}KRADZIEJ [{RANK:>2}]  l_c={lamport_clk:<3}  {msg}{colors[0]}")


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
    log(lamport_clk, f"Wysyla REQ,1,{lamport_clk} do wszystkich")
    for dest_id in range(K):
        if dest_id != RANK:
            comm.send(f"REQ,{critical_section_number},{lamport_clk}", dest=dest_id)


def send_ack(critical_section_number, dest_id, lamport_clk):
    log(lamport_clk, f"Odsylam ACK,{critical_section_number} do [{dest_id}]")
    comm.send(f"ACK,{critical_section_number},{lamport_clk}", dest=dest_id)


def charge_equipment():
    print("Sprzet laduje sie")
    time.sleep(EQUIPMENT_CHARGING_TIME)
    print("Sprzet naladowany")
    for dest_id in range(K):
        comm.send("RELEASE,1,0", dest=dest_id)






if __name__ == "__main__":

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

    # INICJACJA ZMIENNYCH KRADZIEJA
    lamport_clk = 0  # Zegar lamporta procesu kradzieja
    cs_flag_1 = "Init"  # Flaga procesu kradzieja dla PIERWSZEJ sekcji krytycznej
    cs_flag_2 = "Init"  # Flaga procesu kradzieja dla DRUGIEJ sekcji krytycznej
    equipment_amount = S  # Aktualna pamiętana ilość dostępnych sprzętów (może być ujemna!)
    requests_queue = []  # Kolejka requestów
    log(lamport_clk, "Init")

    while True:

        # ROZESŁANIE REQUESTÓW DO WSZYSTKICH ODNOŚNIE #1 SEKCJI
        if cs_flag_1 == "Init" or cs_flag_1 == "Released":
            log(lamport_clk, "CS_FLAG #1 = Wanted")
            cs_flag_1 = "Wanted"
            send_request(1, lamport_clk)
            continue

        # ZARZĄDZANIEM WIADOMOŚCIAMI PRZED WEJŚCIEM DO #1 SEKCJI
        if cs_flag_1 == "Wanted":

            ack_amount = 0  # Ilość otrzymanych ACK
            while ack_amount < K - S:

                messages = get_messages()
                for message in messages:
                    log(lamport_clk, f"Wiadomosc {message}")
                    author = message[0]
                    content = message[1].split(",")
                    # content[0]: Typ wiadomości
                    # content[1]: Której sekcji dotyczy
                    # content[2]: Zegar lamporta autora

                    if content[0] == "REQ" and content[1] == "1":
                        if int(content[2]) < lamport_clk or (int(content[2]) == lamport_clk and int(author) < RANK):
                            lamport_clk += 1
                            send_ack(1, int(author), lamport_clk)
                            equipment_amount -= 1
                        else:
                            log(lamport_clk, f"Kolejka + {message}")
                            requests_queue.append(message)
                        continue

                    if content[0] == "ACK" and content[1] == "1":
                        log(lamport_clk, f"Dostal ACK od {author}")
                        ack_amount += 1
                        continue

                    if content[0] == "RELEASE":
                        equipment_amount += 1
                        continue

            '''while equipment_amount <= 0:
                messages = get_messages()
                for message in messages:
                    author = message[0]
                    content = message[1].split(",")
                    if content[0] == "RELEASE":
                        equipment_amount += 1
                        break
                    else:
                        continue'''

            cs_flag_1 = "Held"

        # 1. SEKCJA KRYTYCZNA
        if cs_flag_1 == "Held":

            log(lamport_clk, "JESTEM W SEKCJI KRYTYCZNEJ #01")
            # S E K C J A   K R Y T Y C Z N A
            log(lamport_clk, "WYCHODZE Z SEKCJI KRYTYCZNEJ #01")
            cs_flag_1 = "Released"
            lamport_clk += 1

            messages = get_messages()
            for message in messages:
                requests_queue.append(message)
            for message in requests_queue:
                log(lamport_clk, f"Wiadomosc {message}")
                author = message[0]
                content = message[1].split(",")

                if content[0] == "REQ" and content[1] == "1":
                    send_ack(1, int(author), lamport_clk)
                    if int(content[2]) >= lamport_clk:
                        lamport_clk = int(content[2])
                    equipment_amount -= 1

            requests_queue = []





        # KRĄŻENIE PO MIEŚCIE
        if cs_flag_1 == "Released":
            good_mood_found = False
            while not good_mood_found:
                city_circulation_time = random.randint(CITY_CIRCULATION_TIME[0], CITY_CIRCULATION_TIME[1])
                log(lamport_clk, f"Rozpoczyna krazenie po miescie przez ({city_circulation_time} s)")
                time.sleep(city_circulation_time)
                if random.random() < GOOD_MOOD_PROBABILITY:
                    good_mood_found = True
                    log(lamport_clk, "Zlapal dobry humor!")


        # 2. SEKCJA KRYTYCZNA (dostęp do laboratorium)
        if cs_flag_2 == "Init" or cs_flag_2 == "Released":
            log(lamport_clk, "CS_FLAG #2 = Wanted")
            cs_flag_2 = "Wanted"
            send_request(2, lamport_clk)
            # continue

        # ZARZĄDZANIE WIADOMOŚCIAMI PRZED WEJŚCIEM DO SEKCJI KRYTYCZNEJ #2
        if cs_flag_2 == "Wanted":

            ack_amount = 0  # Ilość otrzymanych ACK
            while ack_amount < K - N:

                messages = get_messages()
                for message in messages:
                    log(lamport_clk, f"Wiadomosc {message}")
                    author = message[0]
                    content = message[1].split(",")
                    # content[0]: Typ wiadomości
                    # content[1]: Której sekcji dotyczy
                    # content[2]: Zegar lamporta autora

                    if content[0] == "REQ" and content[1] == "2":
                        if int(content[2]) < lamport_clk or (int(content[2]) == lamport_clk and int(author) < RANK):
                            lamport_clk += 1
                            send_ack(2, int(author), lamport_clk)
                        else:
                            log(lamport_clk, f"Kolejka + {message}")
                            requests_queue.append(message)
                        continue

                    if content[0] == "ACK" and content[1] == "2":
                        log(lamport_clk, f"Dostal ACK od {author}")
                        ack_amount += 1
                        continue

                    '''if content[0] == "RELEASE":
                        equipment_amount += 1
                        continue'''

            cs_flag_2 = "Held"

        # 2. SEKCJA KRYTYCZNA (dostęp do laboratorium)
        if cs_flag_2 == "Held":

            log(lamport_clk, "JESTEM W SEKCJI KRYTYCZNEJ #02")
            # S E K C J A   K R Y T Y C Z N A (dostęp do laboratorium)
            log(lamport_clk, "WYCHODZE Z SEKCJI KRYTYCZNEJ #02")

            messages = get_messages()
            for message in messages:
                requests_queue.append(message)
            for message in requests_queue:
                log(lamport_clk, f"Wiadomosc {message}")
                author = message[0]
                content = message[1].split(",")

                if content[0] == "REQ" and content[1] == "2":
                    send_ack(2, int(author), lamport_clk)
                    if int(content[2]) >= lamport_clk:
                        lamport_clk = int(content[2])
                    lamport_clk += 1
            requests_queue = []

            cs_flag_2 = "Released"
            charge_equipment()
            equipment = threading.Thread(target=charge_equipment, name='equipment')
            equipment.start()
            equipment.join()


        # exit()

