# Zadanie 3 — prosty RAG (baza wiedzy + Claude)

Konsolowa aplikacja RAG (Retrieval-Augmented Generation): baza wiedzy w
bazie wektorowej (ChromaDB), embeddingi liczone przez Voyage AI, odpowiedzi
generowane przez Claude na podstawie znalezionych fragmentów.

## Instalacja

```bash
pip install -r requirements.txt
```

## Konfiguracja kluczy API

Potrzebne są **dwa** klucze (Claude nie liczy embeddingów — patrz wyjaśnienie
niżej). Każdy można ustawić lokalnie w tym folderze albo wspólnie w głównym
folderze repozytorium (jeden poziom wyżej), tak jak w poprzednich zadaniach:

| Klucz | Plik lokalny | Plik przykładowy | Skąd wziąć |
|---|---|---|---|
| Anthropic (Claude) | `api_key.txt` | `api_key.example.txt` | [platform.claude.com](https://platform.claude.com) |
| Voyage AI (embeddingi) | `voyage_api_key.txt` | `voyage_api_key.example.txt` | [voyageai.com](https://www.voyageai.com) (darmowy tier) |

## Uruchomienie

```bash
python3 rag.py
```

Pokaże się menu:

```
1. Dodaj wiedze z pliku tekstowego
2. Dodaj wiedze - wpisz tekst recznie (custom)
3. Zadaj pytanie do bazy wiedzy
4. Pokaz liczbe fragmentow w bazie
5. Wyjdz
```

- **Opcja 1** — podajesz ścieżkę do pliku `.txt`, jego zawartość jest
  dzielona na fragmenty (akapity oddzielone pustą linią) i dodawana do bazy.
- **Opcja 2 (custom)** — wpisujesz lub wklejasz tekst ręcznie wprost w
  terminalu (bez potrzeby pliku), kończysz wpisując `KONIEC` w nowej linii.
  Możesz nadać temu wpisowi tytuł/źródło — przydatne np. do dopisania
  własnej notatki albo wklejenia fragmentu ze strony internetowej.
- **Opcja 3** — zadajesz pytanie; aplikacja liczy embedding pytania,
  wyszukuje 3 najbardziej pasujące fragmenty w bazie wektorowej i wysyła je
  jako kontekst do Claude, które odpowiada na tej podstawie (i mówi wprost,
  gdy nie znajdzie odpowiedzi w bazie).

Baza wektorowa zapisuje się na dysku w folderze `baza_wektorowa/` (nie jest
śledzona przez git) — dane zostają między uruchomieniami skryptu.

## Dlaczego dwa klucze / dwa serwisy?

Anthropic (Claude) nie oferuje własnego modelu do embeddingów — do tego
używamy Voyage AI (oficjalnie rekomendowanego przez Anthropic). Podział ról:

- **Voyage AI** → zamienia tekst na wektor liczbowy (embedding) i wyszukuje
  podobieństwo semantyczne w ChromaDB.
- **Claude** → dostaje znalezione fragmenty jako kontekst i generuje
  odpowiedź w naturalnym języku.
