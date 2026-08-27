# Zadanie 2 — zgłoszenie usterki żarówki (function calling)

Czat z Claude, który zadaje maksymalnie 3 pytania diagnostyczne, aby ustalić
czy żarówka jest uszkodzona. Jeśli tak — wywołuje function calling (narzędzie
`zapisz_zgloszenie`), które zapisuje opis usterki do pliku `zgloszenia.txt`.

## Instalacja

```bash
pip install -r requirements.txt
```

## Konfiguracja klucza API

Tak samo jak w `zad1` — klucz można wkleić lokalnie do `api_key.txt` w tym
folderze, albo wspólnie do `api_key.txt` w głównym folderze repozytorium
(jeden poziom wyżej), skąd korzystają wszystkie zadania.

## Uruchomienie

```bash
python3 zgloszenie.py
```

Opisz problem z żarówką, a następnie odpowiadaj na kolejne pytania Claude.
Jeśli model uzna żarówkę za uszkodzoną, zapisze zgłoszenie do
`zgloszenia.txt` w tym folderze (plik nie jest śledzony przez git).

## Jak to działa

- `TOOLS` w `zgloszenie.py` definiuje narzędzie `zapisz_zgloszenie` (opis +
  schemat wejścia `opis: string`).
- System prompt instruuje model, żeby zadał dokładnie 3 pytania, po jednym
  na wiadomość, a potem podjął decyzję.
- Ręczna pętla agentowa (`client.messages.create` w `while`/`for`) sprawdza
  `stop_reason`: `tool_use` → wykonaj `zapisz_zgloszenie()` w Pythonie i
  odeślij wynik jako `tool_result`; `end_turn` → wypisz pytanie/odpowiedź i
  poczekaj na kolejną wiadomość użytkownika.
