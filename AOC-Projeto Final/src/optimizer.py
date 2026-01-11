import re

PIPELINE_STAGES = 5

def parse_instruction(instr):
    instr = instr.replace(",", "")
    parts = instr.split()
    opcode = parts[0].upper()
    regs = parts[1:]
    return opcode, regs

def detect_dependencies(instructions):
    """
    Detecta dependências RAW, WAR e WAW
    """
    last_write = {}
    dependencies = []

    for idx, instr in enumerate(instructions):
        opcode, regs = parse_instruction(instr)

        if len(regs) == 0:
            continue

        dest = regs[0]
        sources = regs[1:]

        # RAW
        for src in sources:
            if src in last_write:
                dependencies.append((idx, last_write[src], "RAW"))

        # WAW
        if dest in last_write:
            dependencies.append((idx, last_write[dest], "WAW"))

        # WAR
        for reg, w_idx in last_write.items():
            if reg in sources:
                dependencies.append((idx, w_idx, "WAR"))

        last_write[dest] = idx

    return dependencies

def insert_nops(instructions, dependencies):
    optimized = []
    last_hazard = set([d[0] for d in dependencies])

    for idx, instr in enumerate(instructions):
        optimized.append(instr)
        if idx in last_hazard:
            optimized.append("NOP")

    return optimized

def reorder_instructions(instructions):
    """
    Reorganização simples:
    move instruções independentes para preencher bolhas
    """
    reordered = instructions.copy()

    for i in range(len(reordered) - 1):
        op1, r1 = parse_instruction(reordered[i])
        op2, r2 = parse_instruction(reordered[i+1])

        if len(r1) > 0 and len(r2) > 0:
            if r1[0] not in r2 and r2[0] not in r1:
                reordered[i], reordered[i+1] = reordered[i+1], reordered[i]

    return reordered

def estimate_cycles(instructions):
    return len(instructions) + PIPELINE_STAGES - 1

def load_mips_file(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    file_path = "../mips_codes/codigo_A.txt"
    instructions = load_mips_file(file_path)

    print("Código original:")
    for i in instructions:
        print(i)

    deps = detect_dependencies(instructions)
    print("\nDependências detectadas:")
    for d in deps:
        print(d)

    reordered = reorder_instructions(instructions)
    nop_inserted = insert_nops(reordered, deps)

    print("\nCódigo otimizado:")
    for i in nop_inserted:
        print(i)

    original_cycles = estimate_cycles(instructions)
    optimized_cycles = estimate_cycles(nop_inserted)

    print("\nCiclos estimados:")
    print("Original:", original_cycles)
    print("Otimizado:", optimized_cycles)

if __name__ == "__main__":
    main()
