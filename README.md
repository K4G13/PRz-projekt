# Kradzieje nastrojów 👤

## ∙ Treść zadania 📜
Po ulicach krążą kradzieje nastrojów. Gdy tylko dostrzegą kogoś w dobrym humorze, natychmiast mu ten dobry humor kradną i zwiewają do laboratorium, gdzie przerabiają ukradziony humor na nielegalną gumę do żucia. <br>
Danych jest K kradziejów. Dostępne są nierozróżnialne zasoby S sprzętu do kradziejowania nastrojów oraz Laboratorium z N nierozróżnialnych stanowisk. Kradziej pobiera 1 sprzęt, następnie losowy czas krąży po mieście. Losowo może odnajdzie kogoś z dobrym nastrojem i wtedy zajmuje 1 stanowisko w laboratorium. Sprzęt po użyciu nie jest zwalniany od razu - jest odkładany i jakiś czas nabiera mocy, zanim wróci do puli dostępnych zasobów.

## ∙ Algorytm 👾
<ol>
    <li>
        <b>Inicjalizacja</b>
        <ul>
            <li>Ilość kradziejów: K</li>
            <li>Ilość nierozróżnialnego sprzętu do kradzenia nastroju: S</li>
            <li>Ilość nierozróżnialnych miejsc w laboratorium: N</li>
            <li>Czas ładowania sprzętu: T</li>
            <li>Czas krążenia po mieście: od X do Y</li>
            <li>Prawdopodobieństwo znalezienia dobrego humoru: P</li>
        </ul>
    </li>
    <li>
        <b>Dostęp do sekcji krytycznej</b>
        <ol>
            <li>
                Każdy proces posiada zegar który przy inicjacji jest ustawiony na 0 oraz dwie flagi oznaczające chęci dostępu od sekcji krytycznych
            </li>
            <li>
                Enter(Nr_sekcji_krytycznej)
                <ul>
                    <li>Flaga statusu danej sekcji := “Wanted”</li>
                    <li>Multicast Request’u [Nr_sekcji_krytycznej, Czas_Lamport’a, ID_procesu] do wszystkich innych procesów kradziejów</li>
                    <li>Oczekiwanie na odpowiedź od (K-wielkość_sekcji_krytycznej) procesów</li>
                    <li>Flaga statusu danej sekcji := “Held”</li>
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
                            ALBO
                            <li>-//- == “Wanted” ORAZ zegar procesu jest większy od wartości zegara w Requeście (jeżeli są te same to zamiast wartości zegara bierzemy ID_procesów) )</li>
                        </ul>
                        Dodaj dany request do lokalnej kolejki procesu
                    </li>
                    <li>
                        Jeżeli nie
                        <ul>
                            <li>Zegar := zegar + 1</li>
                            <li>Odeślij potwierdzenie zawierające obecną wartość zegara oraz ID_procesu</li>
                        </ul>
                    </li>
                </ul>
            </li> 
            <li>
                Exit()
                <ul>
                    <li>Wyjście z sekcji krytycznej</li>
                    <li>Flaga statusu danej sekcji := “Released”</li>
                    <li>Zegar := max(zegary_zakolejkowanych_requestów) + 1</li>
                    <li>Odeślij potwierdzenia zawierające obecną wartość zegara oraz ID_procesu do wszystkich zakolejkowanych “Requestów” w lokalnej kolejce</li>
                </ul>
            </li> 
        </ol>
    </li>
    <li>
        <b>Pobranie sprzętu</b>
        <ol>
            <li>Proces próbuje się dostać do PIERWSZEJ sekcji krytycznej (Krok 2: Enter)</li>
            <li>Przejście do kroku 4.</li>
        </ol>
    </li>
    <li>
        <b>Krążenie po mieście</b>
        <ol>
            <li>Proces losuje czas krążenia po mieście z zakresu od X do Y</li>
            <li>Proces zasypia na wylosowany czas</li>
            <li>
                Proces ma P prawdopodobieństwo na znalezienie osoby z dobrym nastrojem
                <ul>
                    <li>Jeżeli taką osobę znajdzie to przechodzi do kroku 5.</li>
                    <li>Jeżeli nie, powtarza krok 4.</li>
                </ul>
            </li>
        </ol>
    </li>
    <li>
        <b>Dostęp do laboratorium</b>
        <ol>
            <li>Proces próbuje się dostać do DRUGIEJ sekcji krytycznej (Krok 2: Enter)</li>
            <li>Kradziej przerabia humor na gumę do żucia</li>
            <li>Proces wychodzi z DRUGIEJ sekcji krytycznej (Krok 2: Exit)</li>
            <li>Proces tworzy wątek, który przechodzi do kroku 6. natomiast sam proces przechodzi do kroku 3.</li>
        </ol>
    </li>
    <li>
        <b>Ładowanie sprzętu</b>
        <ol>
            <li>Wątek zasypia na T czasu</li>
            <li>Wątek wychodzi z PIERWSZEJ sekcji krytycznej (Krok 2: Exit)</li>
            <li>Wątek kończy swoją egzystencję</li>
        </ol>
    </li>
</ol>

## ∙ Kod albo coś nwm 👩🏻‍💻
