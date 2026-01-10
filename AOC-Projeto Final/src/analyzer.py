def parse_instruction(instr):
    instr = instr.replace(",", "")
    parts = instr.split()

    opcode = parts[0].upper()
    regs = parts[1:] if len(parts) > 1 else []

    dest = None
    sources = []

    # Padrão simples para instruções aritméticas
    if len(regs) >= 1:
        dest = regs[0]
        sources = regs[1:]

    return opcode, dest, sources


def detect_dependencies(instructions):
    """
    Detecta dependências:
    RAW - Read After Write
    WAR - Write After Read
    WAW - Write After Write
    """
    last_write = {}
    last_read = {}
    dependencies = []

    for idx, instr in enumerate(instructions):
        opcode, dest, sources = parse_instruction(instr)

        # Verifica RAW
        for src in sources:
            if src in last_write:
                dependencies.append(
                    (idx, last_write[src], "RAW", src)
                )

        # Verifica WAR
        if dest:
            if dest in last_read:
                dependencies.append(
                    (idx, last_read[dest], "WAR", dest)
                )

        # Verifica WAW
        if dest:
            if dest in last_write:
                dependencies.append(
                    (idx, last_write[dest], "WAW", dest)
                )

        # Atualiza leituras
        for src in sources:
            last_read[src] = idx

        # Atualiza escrita
        if dest:
            last_write[dest] = idx

    return dependencies


def load_mips_file(path):
    with open(path, "r") as file:
        return [line.strip() for line in file if line.strip()]


def main():
    file_path = "../mips_codes/codigo_B.txt"
    instructions = load_mips_file(file_path)

    print("\nCódigo MIPS analisado:\n")
    for i, instr in enumerate(instructions):
        print(f"{i}: {instr}")

    deps = detect_dependencies(instructions)

    print("\nDependências encontradas:\n")
    if not deps:
        print("Nenhuma dependência encontrada.")
    else:
        for dep in deps:
            print(
                f"Instrução {dep[0]} depende da instrução {dep[1]} "
                f"({dep[2]} no registrador {dep[3]})"
            )


if __name__ == "__main__":
    main()
