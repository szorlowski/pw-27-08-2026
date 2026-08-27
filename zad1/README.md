# pw-27-08-2026

## Hello World w Brainfucku

- `hello.bf` — program w Brainfucku wypisujący `Hello World!`
- `interpreter.py` — prosty interpreter Brainfucka w Pythonie

Uruchomienie:

```bash
python3 interpreter.py hello.bf
```

## Czat z Claude (Anthropic API)

Prosta aplikacja czatu w terminalu, korzystająca z oficjalnego SDK `anthropic`.

### Instalacja

```bash
pip install -r requirements.txt
```

### Konfiguracja klucza API

Klucz można ustawić na dwa sposoby (aplikacja sprawdza je w tej kolejności):

**1. Lokalnie (tylko dla tego folderu)**

```bash
cp api_key.example.txt api_key.txt
```

i wklej klucz do `api_key.txt` (jedna linia, sam klucz). Plik jest w
`.gitignore` — nie trafi do repozytorium.

**2. Globalnie (dla wszystkich zadań na tym komputerze)**

Wklej klucz do pliku w swoim folderze domowym — wystarczy zrobić to raz i
każde kolejne zadanie (`zad2`, `zad3`, ...) go znajdzie bez kopiowania:

- Windows: `%USERPROFILE%\.anthropic\api_key.txt`
- Linux/macOS: `~/.anthropic/api_key.txt`

### Uruchomienie

```bash
python3 chat.py
```

Wpisz wiadomość i naciśnij Enter, aby porozmawiać z Claude. Wpisz `exit`, aby zakończyć.
