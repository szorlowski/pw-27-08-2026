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

1. Skopiuj `api_key.example.txt` do `api_key.txt`:
   ```bash
   cp api_key.example.txt api_key.txt
   ```
2. Wklej swój klucz API Anthropic do `api_key.txt` (jedna linia, sam klucz).

Plik `api_key.txt` jest w `.gitignore` — nie trafi do repozytorium.

### Uruchomienie

```bash
python3 chat.py
```

Wpisz wiadomość i naciśnij Enter, aby porozmawiać z Claude. Wpisz `exit`, aby zakończyć.
