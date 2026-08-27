from datetime import datetime
from pathlib import Path

from mcp.server.mcpserver import MCPServer

ZGLOSZENIA_FILE = Path(__file__).parent / "zgloszenia.txt"

mcp = MCPServer("zgloszenia-zarowek")


@mcp.tool(
    description=(
        "Zapisuje zgloszenie awarii zarowki do pliku, gdy na podstawie "
        "wywiadu z uzytkownikiem ustalono, ze zarowka jest uszkodzona."
    )
)
def zapisz_zgloszenie(opis: str) -> str:
    """opis: opis usterki zarowki podsumowujacy wywiad z uzytkownikiem."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with ZGLOSZENIA_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n{opis}\n{'-' * 40}\n")
    return f"Zgloszenie zapisane do {ZGLOSZENIA_FILE.name}."


if __name__ == "__main__":
    mcp.run()
