import sys
from pathlib import Path

import anthropic

MODEL = "claude-opus-5"
MAX_TOKENS = 4096
KEY_FILE = Path(__file__).parent / "api_key.txt"
KEY_EXAMPLE_FILE = Path(__file__).parent / "api_key.example.txt"
GLOBAL_KEY_FILE = Path.home() / ".anthropic" / "api_key.txt"
PLACEHOLDER = "WKLEJ_TUTAJ_SWOJ_KLUCZ_API_ANTHROPIC"


def _read_key(path: Path) -> str:
    key = path.read_text(encoding="utf-8").strip()
    return "" if key == PLACEHOLDER else key


def load_api_key() -> str:
    if KEY_FILE.exists():
        key = _read_key(KEY_FILE)
        if key:
            return key

    if GLOBAL_KEY_FILE.exists():
        key = _read_key(GLOBAL_KEY_FILE)
        if key:
            return key

    sys.exit(
        "Nie znaleziono klucza API. Ustaw go w jeden z dwoch sposobow:\n"
        f"  - lokalnie: skopiuj {KEY_EXAMPLE_FILE.name} do {KEY_FILE.name} "
        "w tym folderze i wklej tam klucz,\n"
        f"  - globalnie (dla wszystkich zadan): wklej klucz do "
        f"{GLOBAL_KEY_FILE}"
    )


def main() -> None:
    client = anthropic.Anthropic(api_key=load_api_key())
    messages = []

    print("Czat z Claude (Anthropic API). Wpisz 'exit' aby zakonczyc.\n")

    while True:
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

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages,
            )
        except anthropic.AuthenticationError:
            sys.exit(
                f"Nieprawidlowy klucz API (sprawdz {KEY_FILE.name} lub "
                f"{GLOBAL_KEY_FILE})."
            )
        except anthropic.RateLimitError:
            print("Przekroczono limit zapytan, sprobuj ponownie za chwile.\n")
            messages.pop()
            continue
        except anthropic.APIStatusError as e:
            print(f"Blad API: {e.message}\n")
            messages.pop()
            continue
        except anthropic.APIConnectionError:
            print("Blad polaczenia sieciowego.\n")
            messages.pop()
            continue

        reply = next((b.text for b in response.content if b.type == "text"), "")
        print(f"Claude: {reply}\n")
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
