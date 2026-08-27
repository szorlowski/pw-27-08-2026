# Zadanie 2 (wersja MCP) — zgłoszenie usterki żarówki

To samo zadanie co w `zad2`, ale zamiast wykonywać narzędzie
`zapisz_zgloszenie` jako zwykłą funkcję Pythona w tym samym procesie,
narzędzie jest wystawione przez **własny serwer MCP** (Model Context
Protocol) i wywoływane przez ten protokół.

## Architektura

```
zgloszenie_mcp.py (klient)  <--- MCP (stdio) --->  mcp_server.py (serwer)
        |                                                  |
        | Claude API (tools=[...])                         | zapisuje do
        v                                                  v
     Anthropic                                       zgloszenia.txt
```

- **`mcp_server.py`** — serwer MCP napisany od zera przy pomocy `MCPServer`
  z pakietu `mcp`. Wystawia jedno narzędzie: `zapisz_zgloszenie(opis: str)`,
  które dopisuje zgłoszenie do `zgloszenia.txt`. Uruchamia się jako osobny
  proces komunikujący się przez stdio (standardowe wejście/wyjście).
- **`zgloszenie_mcp.py`** — klient. Startuje `mcp_server.py` jako podproces
  (`StdioServerParameters` + `stdio_client`), pyta go o liste dostępnych
  narzędzi (`session.list_tools()`) i konwertuje je na format narzędzi
  Claude API (`name`, `description`, `input_schema`). Reszta działa tak
  samo jak w `zad2`: system prompt każe zadać 3 pytania diagnostyczne, a
  gdy Claude zdecyduje że żarówka jest zepsuta, wywołuje narzędzie — tyle
  że wykonanie idzie teraz przez `session.call_tool(...)` (żądanie MCP do
  osobnego procesu), a nie przez bezpośrednie wywołanie funkcji Pythona.

## Różnica względem `zad2`

| | `zad2` (plain function calling) | `zad2_mcp` (MCP) |
|---|---|---|
| Gdzie żyje funkcja narzędzia | W tym samym pliku/procesie co czat | W osobnym procesie (serwerze MCP) |
| Jak jest wywoływana | Zwykłe wywołanie Pythona `zapisz_zgloszenie(opis)` | Żądanie protokołu MCP `session.call_tool(...)` przez stdio |
| Skąd bierze się lista narzędzi | Ręcznie zdefiniowana stała `TOOLS` w kliencie | Pobierana dynamicznie z serwera (`list_tools()`) |
| Zalety MCP | Serwer można współdzielić między wieloma klientami/projektami, uruchamiać osobno, testować niezależnie, podłączyć też do innych aplikacji obsługujących MCP (np. Claude Desktop) | |

## Instalacja

```bash
pip install -r requirements.txt
```

## Konfiguracja klucza API

Tak samo jak w `zad1`/`zad2` — lokalnie w `api_key.txt` w tym folderze, albo
wspólnie w `api_key.txt` w głównym folderze repozytorium (jeden poziom
wyżej).

## Uruchomienie

```bash
python3 zgloszenie_mcp.py
```

Nie trzeba osobno startować `mcp_server.py` — klient uruchamia go
automatycznie jako podproces. Opisz problem z żarówką i odpowiadaj na
pytania Claude. Jeśli model uzna żarówkę za uszkodzoną, zgłoszenie trafi do
`zgloszenia.txt` w tym folderze (plik nie jest śledzony przez git).
