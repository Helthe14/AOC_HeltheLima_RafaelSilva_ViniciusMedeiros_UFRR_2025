# Otimização de Códigos MIPS em Processadores com Pipeline

Projeto final da disciplina Arquitetura e Organização de Computadores – UFRR.

## 🎯 Objetivo

Desenvolver um sistema em Python capaz de analisar trechos de código MIPS, identificar dependências de dados e aplicar técnicas de otimização para reduzir bolhas no pipeline, melhorando o throughput da execução.

## 🧠 Funcionalidades

- Leitura automática de arquivos contendo código MIPS.
- Identificação de dependências RAW, WAR e WAW.
- Reorganização simples de instruções independentes.
- Inserção automática de instruções NOP quando necessário.
- Estimativa do número de ciclos em um pipeline de 5 estágios.
- Execução automática de testes para múltiplos códigos.

## 📁 Estrutura do Projeto

AOC_Helthe_UFRR_2025
│
├── src/
│ ├── analyzer.py
│ ├── optimizer.py
│ └── run_all_tests.py
│
├── mips_codes/
│ ├── codigo_A.txt
│ ├── codigo_B.txt
│ ├── codigo_C.txt
│ ├── codigo_D.txt
│ ├── codigo_E.txt
│ └── codigo_F.txt
│
├── results/
│ └── resultados.txt
│
└── README.md


## ▶️ Como Executar

### Requisitos
- Python 3.9 ou superior
- Sistema operacional: Windows / Linux / MacOS
- IDE utilizada: Visual Studio Code

### Execução dos testes

No terminal:

```bash
cd src
python run_all_tests.py

O arquivo de resultados será gerado em:
results/resultados.txt

🛠️ Tecnologias

Python

Visual Studio Code

GitHub

👨‍🎓 Autor

Helthe Magalhães – Ciência da Computação – UFRR