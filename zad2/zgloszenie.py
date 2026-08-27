import json
import sys
from datetime import datetime
from pathlib import Path

import anthropic

MODEL = "claude-opus-5"
MAX_TOKENS = 4096
MAX_TURNS = 6  # zabezpieczenie przed niekonczaca sie rozmowa

KEY_FILE = Path(__file__).parent / "api_key.txt"
KEY_EXAMPLE_FILE = Path(__file__).parent / "api_key.example.txt"
ROOT_KEY_FILE = Path(__file__).parent.parent / "api_key.txt"
PLACEHOLDER = "WKLEJ_TUTAJ_SWOJ_KLUCZ_API_ANTHROPIC"

ZGLOSZENIA_FILE = Path(__file__).parent / "zgloszenia.txt"

SYSTEM_PROMPT = """Jestes asystentem serwisowym diagnozujacym usterki zarowek.

Twoje zadanie:
1. Zadaj uzytkownikowi dokladnie 3 pytania diagnostyczne, PO JEDNYM na wiadomosc
   (czekaj na odpowiedz przed zadaniem kolejnego), aby ustalic czy zarowka
   faktycznie jest uszkodzona. Przykladowe kierunki pytan: czy zarowka w ogole
   sie swieci, czy sprawdzono ja w innym gniazdku/oprawce, czy miga/przygasa
   albo czy widac/slychac oznaki przepalenia (np. sczerniala baneczka,
   grzechotanie druciku).
2. Po trzeciej odpowiedzi podejmij decyzje:
   - Jesli na podstawie odpowiedzi uznasz, ze zarowka jest uszkodzona,
     wywolaj narzedzie 'zapisz_zgloszenie' z opisem usterki podsumowujacym
     rozmowe, a nastepnie potwierdz uzytkownikowi ze zgloszenie zostalo
     zapisane.
   - Jesli uznasz, ze zarowka nie jest uszkodzona (np. problem lezy gdzie
     indziej), NIE wywoluj narzedzia - wyjasnij uzytkownikowi wnioski i
     zaproponuj inne rozwiazanie.
Nie zadawaj wiecej niz 3 pytan diagnostycznych."""

TOOLS = [
    {
        "name": "zapisz_zgloszenie",
        "description": (
            "Zapisuje zgloszenie awarii zarowki do pliku, gdy na podstawie "
            "wywiadu z uzytkownikiem ustalono, ze zarowka jest uszkodzona."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "opis": {
                    "type": "string",
                    "description": (
                        "Opis usterki zarowki podsumowujacy rozmowe z "
                        "uzytkownikiem."
                    ),
                }
            },
            "required": ["opis"],
            "additionalProperties": False,
        },
    }
]


def _read_key(path: Path) -> str:
    key = path.read_text(encoding="utf-8").strip()
    return "" if key == PLACEHOLDER else key


def load_api_key() -> str:
    if KEY_FILE.exists():
        key = _read_key(KEY_FILE)
        if key:
            return key

    if ROOT_KEY_FILE.exists():
        key = _read_key(ROOT_KEY_FILE)
        if key:
            return key

    sys.exit(
        "Nie znaleziono klucza API. Ustaw go w jeden z dwoch sposobow:\n"
        f"  - lokalnie: skopiuj {KEY_EXAMPLE_FILE.name} do {KEY_FILE.name} "
        "w tym folderze i wklej tam klucz,\n"
        f"  - wspolnie dla wszystkich zadan: wklej klucz do pliku "
        f"{ROOT_KEY_FILE.name} w glownym folderze repozytorium "
        f"({ROOT_KEY_FILE})"
    )


def zapisz_zgloszenie(opis: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with ZGLOSZENIA_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n{opis}\n{'-' * 40}\n")
    return f"Zgloszenie zapisane do {ZGLOSZENIA_FILE.name}."


def execute_tool(name: str, tool_input: dict) -> str:
    if name == "zapisz_zgloszenie":
        return zapisz_zgloszenie(tool_input["opis"])
    return f"Nieznane narzedzie: {name}"


def print_text_blocks(content) -> None:
    for block in content:
        if block.type == "text" and block.text.strip():
            print(f"Claude: {block.text}\n")


def main() -> None:
    client = anthropic.Anthropic(api_key=load_api_key())
    messages = []

    print("Zgloszenie usterki zarowki - czat z Claude. Wpisz 'exit' aby przerwac.\n")

    try:
        opis_problemu = input("Ty: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if opis_problemu.lower() in ("exit", "quit") or not opis_problemu:
        return

    messages.append({"role": "user", "content": opis_problemu})

    for _ in range(MAX_TURNS):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            sys.exit(
                f"Nieprawidlowy klucz API (sprawdz {KEY_FILE.name} lub "
                f"{ROOT_KEY_FILE})."
            )
        except anthropic.APIStatusError as e:
            sys.exit(f"Blad API: {e.message}")
        except anthropic.APIConnectionError:
            sys.exit("Blad polaczenia sieciowego.")

        messages.append({"role": "assistant", "content": response.content})
        print_text_blocks(response.content)

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if tool_use_blocks:
            tool_results = []
            for tool in tool_use_blocks:
                print(f"[wywolanie narzedzia: {tool.name}({json.dumps(tool.input, ensure_ascii=False)})]\n")
                result = execute_tool(tool.name, tool.input)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": tool.id, "content": result}
                )
            messages.append({"role": "user", "content": tool_results})
            continue

        if response.stop_reason == "end_turn":
            try:
                user_input = input("Ty: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})
    else:
        print("Osiagnieto limit tury rozmowy.")


if __name__ == "__main__":
    main()
