import sys


def run(code: str) -> None:
    tape = [0] * 30000
    ptr = 0
    pc = 0
    loop_stack = []
    bracket_map = {}

    stack = []
    for i, ch in enumerate(code):
        if ch == "[":
            stack.append(i)
        elif ch == "]":
            start = stack.pop()
            bracket_map[start] = i
            bracket_map[i] = start

    while pc < len(code):
        cmd = code[pc]
        if cmd == ">":
            ptr += 1
        elif cmd == "<":
            ptr -= 1
        elif cmd == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif cmd == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif cmd == ".":
            sys.stdout.write(chr(tape[ptr]))
        elif cmd == ",":
            tape[ptr] = ord(sys.stdin.read(1) or "\0")
        elif cmd == "[":
            if tape[ptr] == 0:
                pc = bracket_map[pc]
        elif cmd == "]":
            if tape[ptr] != 0:
                pc = bracket_map[pc]
        pc += 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uzycie: python3 interpreter.py <plik.bf>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="ascii") as f:
        source = f.read()

    run(source)
