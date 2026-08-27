import sys
from pathlib import Path

import anthropic

MODEL = "claude-opus-5"
MAX_TOKENS = 4096
KEY_FILE = Path(__file__).parent / "api_key.txt"
KEY_EXAMPLE_FILE = Path(__file__).parent / "api_key.example.txt"


def load_api_key() -> str:
    if not KEY_FILE.exists():
        sys.exit(
            f"Brak pliku {KEY_FILE.name}. Skopiuj {KEY_EXAMPLE_FILE.name} do "
            f"{KEY_FILE.name} i wklej tam swoj klucz API Anthropic."
        )

    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key or key == KEY_EXAMPLE_FILE.read_text(encoding="utf-8").strip():
        sys.exit(f"Wklej prawdziwy klucz API do {KEY_FILE.name}.")

    return key


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
            sys.exit(f"Nieprawidlowy klucz API w {KEY_FILE.name}.")
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
