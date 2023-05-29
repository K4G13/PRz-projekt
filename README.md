# Kradzieje nastrojów 👤

## ∙ Treść zadania 📜
Po ulicach krążą kradzieje nastrojów. Gdy tylko dostrzegą kogoś w dobrym humorze, natychmiast mu ten dobry humor kradną i zwiewają do laboratorium, gdzie przerabiają ukradziony humor na nielegalną gumę do żucia. <br>
Danych jest K kradziejów. Dostępne są nierozróżnialne zasoby S sprzętu do kradziejowania nastrojów oraz Laboratorium z N nierozróżnialnych stanowisk. Kradziej pobiera 1 sprzęt, następnie losowy czas krąży po mieście. Losowo może odnajdzie kogoś z dobrym nastrojem i wtedy zajmuje 1 stanowisko w laboratorium. Sprzęt po użyciu nie jest zwalniany od razu - jest odkładany i jakiś czas nabiera mocy, zanim wróci do puli dostępnych zasobów.

## ∙ Algorytm 👾
<ol>
    <li>
        <b>Inicjalizacja</b>
        <ul>
            <li>Ilość kradziejów: <b>K</b></li>
            <li>Ilość nierozróżnialnego sprzętu do kradzenia nastroju: <b>S</b></li>
            <li>Ilość nierozróżnialnych miejsc w laboratorium: <b>N</b></li>
            <li>Czas ładowania sprzętu: <b>T</b></li>
            <li>Czas krążenia po mieście: <b>[X,Y)</b></li>
            <li>Prawdopodobieństwo znalezienia dobrego humoru: <b>P</b></li>
        </ul>
    </li>
    <li>
        <b>Dostęp do sekcji krytycznej</b>
        <ol>
            <li>
                Każdy proces posiada <b>zegar</b> który przy inicjacji jest ustawiony na 0 oraz <b>dwie flagi</b> oznaczające chęci dostępu od sekcji krytycznych oraz zmienną lokalną <b>ilość_sprzętów</b> równą <b>S</b> przy inicjacji
            </li>
            <li>
                Enter(Nr_sekcji_krytycznej)
                <ul>
                    <li>Flaga statusu danej sekcji := <b>“Wanted”</b></li>
                    <li>Multicast Request’u <b>[Nr_sekcji_krytycznej, Czas_Lamport’a, ID_procesu]</b> do wszystkich innych procesów kradziejów</li>
                    <li>Oczekiwanie na odpowiedź od <b>(K-wielkość_sekcji_krytycznej)</b> procesów <b>ORAZ</b> <b>ilość_sprzętów > 0</b></li>
                    <li>Flaga statusu danej sekcji := <b>“Held”</b></li>
                    <li><b>Ilość_sprzętów := ilość_sprzętów - 1</b></li>
                    <li>Wejście do sekcji krytycznej</li>
                </ul>
            </li>
            <li>
                Odbiór “Request”’a
                <ul>
                    <li>
                        Jeżeli (
                        <ul>
                            <li>Status procesu dla danej sekcji krytycznej == “Held”</li>
                            <b>ALBO</b>
                            <li>-//- == “Wanted” ORAZ zegar procesu jest większy od wartości zegara w Requeście (jeżeli są te same to zamiast wartości zegara bierzemy ID_procesów) )</li>
                        </ul>
                        Dodaj dany request do lokalnej kolejki procesu
                    </li>
                    <li>
                        Jeżeli nie
                        <ul>
                            <li><b>Zegar := zegar + 1</b></li>
                            <li>Odeślij potwierdzenie zawierające obecną wartość zegara oraz ID_procesu</li>
                            <li><b>Ilość_sprzętów := ilość_sprzętów - 1</b></li>
                        </ul>
                    </li>
                </ul>
            </li> 
            <li>
                Odbiór “Release”’a 
                <ul>
                    <li><b>Ilość_sprzętów := ilość_sprzętów + 1</b></li>
                </ul>               
            </li> 
            <li>
                Exit()
                <ul>
                    <li>Wyjście z sekcji krytycznej</li>
                    <li>Flaga statusu danej sekcji := <b>“Released”</b></li>
                    <li>Zegar := <b>max(zegary_zakolejkowanych_requestów) + 1</b></li>
                    <li><b>Ilość_sprzętów := ilość_sprzętów - ILOŚĆ REQUESTÓW W KOLEJCE</b></li>
                    <li>Odeślij potwierdzenia zawierające obecną wartość zegara oraz ID_procesu do wszystkich zakolejkowanych “Requestów” w lokalnej kolejce</li>
                </ul>
            </li> 
        </ol>
    </li>
    <li>
        <b>Pobranie sprzętu</b>
        <ol>
            <li>Proces próbuje się dostać do PIERWSZEJ sekcji krytycznej <b>(Krok 2: Enter)</b></li>
            <li>Przejście do <b>kroku 4</b></li>
        </ol>
    </li>
    <li>
        <b>Krążenie po mieście</b>
        <ol>
            <li>Proces losuje czas krążenia po mieście z zakresu <b>[X,Y)</b></li>
            <li>Proces zasypia na wylosowany czas</li>
            <li>
                Proces ma <b>P</b> prawdopodobieństwo na znalezienie osoby z dobrym nastrojem
                <ul>
                    <li>Jeżeli taką osobę znajdzie to przechodzi do <b>kroku 5</b></li>
                    <li>Jeżeli nie, powtarza <b>krok 4</b></li>
                </ul>
            </li>
        </ol>
    </li>
    <li>
        <b>Dostęp do laboratorium</b>
        <ol>
            <li>Proces próbuje się dostać do DRUGIEJ sekcji krytycznej <b>(Krok 2: Enter)</b></li>
            <li>Kradziej przerabia humor na gumę do żucia</li>
            <li>Proces wychodzi z DRUGIEJ sekcji krytycznej <b>(Krok 2: Exit)</b></li>
            <li>Proces tworzy wątek, który przechodzi do <b>kroku 6.</b> natomiast sam proces przechodzi do <b>kroku 3.</b></li>
        </ol>
    </li>
    <li>
        <b>Ładowanie sprzętu</b>
        <ol>
            <li>Wątek zasypia na <b>T</b> czasu</li>
            <li>Wątek wychodzi z PIERWSZEJ sekcji krytycznej <b>(Krok 2: Exit) + wysyła sygnał Release do wszystkich włącznie ze swoim oryginalnym procesem</b></li>
            <li>Wątek kończy swoją egzystencję</li>
        </ol>
    </li>
</ol>

## ∙ Uruchamianie programu 👩🏻‍💻
```
    mpiexec -n <ilość_procesów_kradziejów> python -B main.py <ilość_sprzętów> <ilość_miejsc_w_laboratorium>
```
```
    mpiexec -n 4 python -B main.py 2 3
```

## ∙ Uruchamianie programu 2 👩🏻‍💻
```
    python3 -m venv ~/myenv

    source ~/myenv/bin/activate

    mpiexec -n 4 -hostfile hostfile python -B main.py 3 2 
```