import sys
import uuid
from datetime import datetime
from pathlib import Path

import anthropic
import chromadb
import voyageai

MODEL = "claude-opus-5"
MAX_TOKENS = 4096
EMBED_MODEL = "voyage-4"
N_RESULTS = 3

ANTHROPIC_KEY_FILE = Path(__file__).parent / "api_key.txt"
ANTHROPIC_KEY_EXAMPLE_FILE = Path(__file__).parent / "api_key.example.txt"
ANTHROPIC_ROOT_KEY_FILE = Path(__file__).parent.parent / "api_key.txt"

VOYAGE_KEY_FILE = Path(__file__).parent / "voyage_api_key.txt"
VOYAGE_KEY_EXAMPLE_FILE = Path(__file__).parent / "voyage_api_key.example.txt"
VOYAGE_ROOT_KEY_FILE = Path(__file__).parent.parent / "voyage_api_key.txt"

CHROMA_PATH = Path(__file__).parent / "baza_wektorowa"
COLLECTION_NAME = "wiedza"
ANTHROPIC_PLACEHOLDER = "WKLEJ_TUTAJ_SWOJ_KLUCZ_API_ANTHROPIC"
VOYAGE_PLACEHOLDER = "WKLEJ_TUTAJ_SWOJ_KLUCZ_API_VOYAGE"

SYSTEM_PROMPT = """Jestes asystentem odpowiadajacym na pytania na podstawie
dostarczonego kontekstu (fragmentow z bazy wiedzy). Odpowiadaj tylko na
podstawie tego kontekstu. Jesli w kontekscie nie ma odpowiedzi, powiedz
wprost, ze nie znalazles odpowiedzi w bazie wiedzy - nie zgaduj."""


def _read_key(path: Path, placeholder: str) -> str:
    key = path.read_text(encoding="utf-8").strip()
    return "" if key == placeholder else key


def load_key(
    local_file: Path, example_file: Path, root_file: Path, label: str, placeholder: str
) -> str:
    if local_file.exists():
        key = _read_key(local_file, placeholder)
        if key:
            return key

    if root_file.exists():
        key = _read_key(root_file, placeholder)
        if key:
            return key

    sys.exit(
        f"Nie znaleziono klucza API {label}. Ustaw go w jeden z dwoch sposobow:\n"
        f"  - lokalnie: skopiuj {example_file.name} do {local_file.name} "
        "w tym folderze i wklej tam klucz,\n"
        f"  - wspolnie dla wszystkich zadan: wklej klucz do pliku "
        f"{root_file.name} w glownym folderze repozytorium ({root_file})"
    )


def chunk_text(text: str) -> list[str]:
    akapity = [a.strip() for a in text.split("\n\n")]
    return [a for a in akapity if a]


def dodaj_do_bazy(collection, vo: voyageai.Client, chunks: list[str], source: str) -> None:
    if not chunks:
        print("Brak tresci do dodania.\n")
        return

    try:
        embeddings = vo.embed(chunks, model=EMBED_MODEL, input_type="document").embeddings
    except Exception as e:
        print(f"Blad podczas liczenia embeddingow (Voyage AI): {e}\n")
        return

    ids = [uuid.uuid4().hex for _ in chunks]
    metadatas = [{"source": source} for _ in chunks]
    collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    print(f"Dodano {len(chunks)} fragment(y/ow) do bazy wiedzy (zrodlo: {source}).\n")


def dodaj_z_pliku(collection, vo: voyageai.Client) -> None:
    sciezka = input("Podaj sciezke do pliku tekstowego: ").strip()
    if not sciezka:
        return

    plik = Path(sciezka)
    if not plik.exists():
        print(f"Plik {plik} nie istnieje.\n")
        return

    try:
        tekst = plik.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("Nie udalo sie odczytac pliku jako tekst UTF-8.\n")
        return

    chunks = chunk_text(tekst)
    dodaj_do_bazy(collection, vo, chunks, source=plik.name)


def dodaj_custom(collection, vo: voyageai.Client) -> None:
    tytul = input("Tytul/zrodlo tego wpisu (Enter = 'custom'): ").strip() or "custom"
    print("Wklej lub wpisz tekst. Zakoncz wpisujac samo 'KONIEC' w nowej linii:")

    linie = []
    while True:
        try:
            linia = input()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if linia.strip() == "KONIEC":
            break
        linie.append(linia)

    tekst = "\n".join(linie).strip()
    if not tekst:
        print("Nie podano zadnego tekstu.\n")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    chunks = chunk_text(tekst)
    dodaj_do_bazy(collection, vo, chunks, source=f"{tytul} ({timestamp})")


def zapytaj(collection, vo: voyageai.Client, client: anthropic.Anthropic) -> None:
    if collection.count() == 0:
        print("Baza wiedzy jest pusta - najpierw dodaj do niej jakis tekst.\n")
        return

    pytanie = input("Pytanie: ").strip()
    if not pytanie:
        return

    try:
        q_emb = vo.embed([pytanie], model=EMBED_MODEL, input_type="query").embeddings[0]
    except Exception as e:
        print(f"Blad podczas liczenia embeddingu pytania (Voyage AI): {e}\n")
        return

    wyniki = collection.query(
        query_embeddings=[q_emb], n_results=min(N_RESULTS, collection.count())
    )
    dokumenty = wyniki["documents"][0]
    zrodla = [m["source"] for m in wyniki["metadatas"][0]]

    kontekst = "\n\n".join(
        f"[Zrodlo: {zrodlo}]\n{dokument}" for zrodlo, dokument in zip(zrodla, dokumenty)
    )

    user_message = f"Kontekst z bazy wiedzy:\n\n{kontekst}\n\nPytanie: {pytanie}"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.AuthenticationError:
        sys.exit(f"Nieprawidlowy klucz API Anthropic (sprawdz {ANTHROPIC_KEY_FILE.name}).")
    except anthropic.APIStatusError as e:
        print(f"Blad API: {e.message}\n")
        return
    except anthropic.APIConnectionError:
        print("Blad polaczenia sieciowego.\n")
        return

    odpowiedz = next((b.text for b in response.content if b.type == "text"), "")
    print(f"\nClaude: {odpowiedz}\n")
    print(f"(na podstawie fragmentow ze zrodel: {', '.join(sorted(set(zrodla)))})\n")


def menu() -> None:
    print("Wybierz opcje:")
    print("  1. Dodaj wiedze z pliku tekstowego")
    print("  2. Dodaj wiedze - wpisz tekst recznie (custom)")
    print("  3. Zadaj pytanie do bazy wiedzy")
    print("  4. Pokaz liczbe fragmentow w bazie")
    print("  5. Wyjdz")


def main() -> None:
    anthropic_key = load_key(
        ANTHROPIC_KEY_FILE,
        ANTHROPIC_KEY_EXAMPLE_FILE,
        ANTHROPIC_ROOT_KEY_FILE,
        "Anthropic",
        ANTHROPIC_PLACEHOLDER,
    )
    voyage_key = load_key(
        VOYAGE_KEY_FILE,
        VOYAGE_KEY_EXAMPLE_FILE,
        VOYAGE_ROOT_KEY_FILE,
        "Voyage AI",
        VOYAGE_PLACEHOLDER,
    )

    client = anthropic.Anthropic(api_key=anthropic_key)
    vo = voyageai.Client(api_key=voyage_key)
    chroma = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = chroma.get_or_create_collection(COLLECTION_NAME, embedding_function=None)

    print("=== Prosty RAG: baza wiedzy + Claude ===\n")

    while True:
        menu()
        wybor = input("> ").strip()

        if wybor == "1":
            dodaj_z_pliku(collection, vo)
        elif wybor == "2":
            dodaj_custom(collection, vo)
        elif wybor == "3":
            zapytaj(collection, vo, client)
        elif wybor == "4":
            print(f"Fragmentow w bazie: {collection.count()}\n")
        elif wybor == "5":
            break
        else:
            print("Nieznana opcja, sprobuj ponownie.\n")


if __name__ == "__main__":
    main()
