import os
import re

# ==============================================================================
# 1. PARSER (Interpreta as instruções)
# ==============================================================================
def parse_instruction(instr):
    # Remove vírgulas e divide
    clean_instr = instr.replace(",", " ")
    parts = clean_instr.split()

    if not parts or parts[0].startswith("#"):
        return None, None, []

    opcode = parts[0].upper()
    regs = parts[1:] if len(parts) > 1 else []

    dest = None
    sources = []

    # Instruções onde o primeiro operando NÃO é destino (Stores e Branches)
    # Ex: S.D F4, 0(R1) -> F4 é fonte, R1 é fonte
    if opcode in ['SW', 'S.D', 'SD', 'SB', 'SH', 'JR', 'BEQ', 'BNE']:
        dest = None
        for r in regs:
            # Limpa parênteses ex: 0(R1) -> pega R1
            match = re.search(r'\$?[\w\.]+', r.split('(')[-1].strip(')'))
            if match: sources.append(match.group(0))

    # Instruções de Load (L.D, LW) - Destino é o 1º, Fonte é o registrador dentro do ()
    elif opcode in ['LW', 'L.D', 'LD', 'LB', 'LH']:
        dest = regs[0]
        if len(regs) > 1:
            match = re.search(r'\((.*?)\)', regs[-1]) # Pega o que está dentro do ()
            if match: sources.append(match.group(1))
            else: sources.append(regs[-1]) 
            
    # Instruções Aritméticas Padrão (ADD, SUB, MUL...)
    else:
        if len(regs) >= 1:
            dest = regs[0]
            sources = regs[1:]

    return opcode, dest, sources

# ==============================================================================
# 2. DETECTOR DE DEPENDÊNCIAS
# ==============================================================================
def detect_dependencies(instructions):
    last_write = {}
    dependencies = []

    for idx, instr in enumerate(instructions):
        opcode, dest, sources = parse_instruction(instr)
        if not opcode: continue

        # Verifica RAW (Read After Write)
        for src in sources:
            if src in last_write:
                writer_idx = last_write[src]
                dist = idx - writer_idx
                # Consideramos conflito se a distância for curta (pipeline)
                if dist < 3:
                    dependencies.append((idx, writer_idx, "RAW", src, dist))

        if dest:
            last_write[dest] = idx

    return dependencies

# ==============================================================================
# 3. OTIMIZADOR (Insere NOPs e Tenta Reordenar)
# ==============================================================================
def optimize_pipeline(instructions):
    optimized_code = []
    pool = [] 
    
    # Pré-processa para facilitar a manipulação
    for instr in instructions:
        op, dest, srcs = parse_instruction(instr)
        if op:
            pool.append({'op': op, 'dest': dest, 'srcs': srcs, 'original': instr})
        else:
            # Mantém comentários/linhas vazias se existirem (opcional)
            pass
    
    reg_ready_cycle = {} # Ciclo em que o registrador estará livre
    current_cycle = 1
    i = 0

    while i < len(pool):
        current = pool[i]
        
        # 1. Verifica bolhas necessárias para a instrução ATUAL
        bubbles_needed = 0
        for src in current['srcs']:
            if src in reg_ready_cycle:
                ready_at = reg_ready_cycle[src]
                if ready_at > current_cycle:
                    bubbles_needed = max(bubbles_needed, ready_at - current_cycle)

        # 2. Tenta REORDENAR (Procura instrução futura independente)
        moved = False
        if bubbles_needed > 0:
            lookahead = min(len(pool), i + 5)
            for j in range(i + 1, lookahead):
                candidate = pool[j]
                
                # Checa conflitos da candidata
                conflict = False
                for s in candidate['srcs']:
                    if s in reg_ready_cycle and reg_ready_cycle[s] > current_cycle:
                        conflict = True; break
                
                # Checa conflito com a instrução atual
                if current['dest'] in candidate['srcs']: conflict = True
                if candidate['dest'] and candidate['dest'] in current['srcs']: conflict = True
                if candidate['dest'] == current['dest']: conflict = True

                if not conflict:
                    optimized_code.append(candidate['original'] + "\t # [REORDENADO]")
                    if candidate['dest']:
                        latency = 3 if candidate['op'] in ['LW', 'L.D', 'LD'] else 2
                        reg_ready_cycle[candidate['dest']] = current_cycle + latency
                    pool.pop(j) 
                    current_cycle += 1
                    bubbles_needed -= 1
                    moved = True
                    break

        # 3. Insere NOPs se ainda precisar
        if not moved and bubbles_needed > 0:
            for _ in range(bubbles_needed):
                optimized_code.append("NOP \t\t # [BOLHA]")
                current_cycle += 1
        
        # 4. Insere a instrução atual (se não foi movida antes)
        if not moved:
            optimized_code.append(current['original'])
            if current['dest']:
                latency = 3 if current['op'] in ['LW', 'L.D', 'LD'] else 2
                reg_ready_cycle[current['dest']] = current_cycle + latency
            i += 1
            current_cycle += 1

    return optimized_code

# ==============================================================================
# 4. LEITURA DE ARQUIVO
# ==============================================================================
def load_mips_file(path):
    try:
        with open(path, "r", encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"[ERRO DE LEITURA] {e}")
        return []

# ==============================================================================
# 5. EXECUÇÃO PRINCIPAL
# ==============================================================================
def main():
    # --- CAMINHO DO SEU ARQUIVO ---
    # O 'r' antes das aspas é obrigatório para caminhos do Windows
    file_path = r"C:\Dev\Analise piperline 2\codigo_piperline\codigo_F.txt"
    
    # Verifica se o arquivo existe antes de tentar abrir
    if not os.path.exists(file_path):
        print(f"[ERRO CRÍTICO] O arquivo não foi encontrado em: {file_path}")
        print("Verifique se o nome da pasta ou do arquivo está correto.")
        return

    # Extrai pasta e nome do arquivo para usar depois
    pasta_origem = os.path.dirname(file_path)
    nome_arquivo = os.path.basename(file_path)

    print(f"--- Processando: {nome_arquivo} ---")
    instructions = load_mips_file(file_path)

    if not instructions:
        return

    # Análise
    print("\n[DEPENDÊNCIAS ENCONTRADAS]")
    deps = detect_dependencies(instructions)
    if not deps:
        print("Nenhuma dependência crítica.")
    else:
        for d in deps:
            print(f"Linha {d[0]} espera por {d[3]} (produzido na {d[1]}). Distância: {d[4]}")

    # Otimização
    print("\n[GERANDO ARQUIVO OTIMIZADO]")
    optimized = optimize_pipeline(instructions)
    
    # Cria o caminho de saída na MESMA PASTA do original
    novo_nome = "otimizado_" + nome_arquivo
    caminho_saida = os.path.join(pasta_origem, novo_nome)
    
    try:
        with open(caminho_saida, "w", encoding='utf-8') as f:
            f.write("\n".join(optimized))
        
        print("-" * 50)
        print("SUCESSO! Código otimizado salvo em:")
        print(caminho_saida)
        print("-" * 50)
        
        # Mostra prévia no terminal
        print("\nPrévia do Código Final:")
        for line in optimized:
            print(line)
            
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    main()