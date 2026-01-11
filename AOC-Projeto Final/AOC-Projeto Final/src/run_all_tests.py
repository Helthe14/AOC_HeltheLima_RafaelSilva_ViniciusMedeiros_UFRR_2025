import os
from optimizer import (
    detect_dependencies,
    reorder_instructions,
    insert_nops,
    estimate_cycles,
    load_mips_file
)

RESULTS_PATH = "../results/resultados.txt"
MIPS_FOLDER = "../mips_codes"


def run_tests():
    files = sorted([
        f for f in os.listdir(MIPS_FOLDER)
        if f.endswith(".txt")
    ])

    with open(RESULTS_PATH, "w", encoding="utf-8") as out:
        for file in files:
            out.write("="*60 + "\n")
            out.write(f"ARQUIVO: {file}\n")
            out.write("="*60 + "\n\n")

            path = os.path.join(MIPS_FOLDER, file)
            instructions = load_mips_file(path)

            out.write("Código original:\n")
            for i, instr in enumerate(instructions):
                out.write(f"{i}: {instr}\n")

            deps = detect_dependencies(instructions)

            out.write("\nDependências detectadas:\n")
            if not deps:
                out.write("Nenhuma dependência encontrada.\n")
            else:
                for d in deps:
                    out.write(
                        f"Instrução {d[0]} depende da {d[1]} "
                        f"({d[2]})\n"
                    )

            reordered = reorder_instructions(instructions)
            optimized = insert_nops(reordered, deps)

            out.write("\nCódigo otimizado:\n")
            for instr in optimized:
                out.write(instr + "\n")

            cycles_original = estimate_cycles(instructions)
            cycles_optimized = estimate_cycles(optimized)

            out.write("\nCiclos estimados:\n")
            out.write(f"Original: {cycles_original}\n")
            out.write(f"Otimizado: {cycles_optimized}\n\n")

    print(" Testes finalizados!")
    print(" Resultados salvos em:", RESULTS_PATH)


if __name__ == "__main__":
    run_tests()
