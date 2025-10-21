"""
sistema_arquivos_encadeado.py

Simulação de gerenciamento de arquivos usando lista encadeada.
Agora com INTERFACE DE LINHA DE COMANDO para o usuário interagir:
- Criar arquivo
- Ler arquivo
- Excluir arquivo
- Exibir disco / diretório / blocos livres

Cada bloco do disco tem 32 bits (16 bits para dado, 16 bits para ponteiro).
"""

from array import array
from typing import Dict, Optional, List, Tuple

# ----------------------------
# Configurações e constantes
# ----------------------------
NUM_BLOCKS = 32
NULL_PTR = 0xFFFF
BLOCK_MASK_16 = 0xFFFF
TYPECODE = 'I'

# ----------------------------
# Estruturas globais
# ----------------------------
disk = array(TYPECODE, [0] * NUM_BLOCKS)
directory: Dict[str, Tuple[int, int]] = {}
free_head: Optional[int] = None
free_size: int = 0

# ----------------------------
# Funções utilitárias
# ----------------------------
def pack_block(data16: int, ptr16: int) -> int:
    """Empacota 16 bits de dados e 16 bits de ponteiro em um inteiro 32 bits."""
    return ((ptr16 & BLOCK_MASK_16) << 16) | (data16 & BLOCK_MASK_16)

def unpack_block(value: int) -> Tuple[int, int]:
    """Desempacota o inteiro 32-bit em (data16, ptr16)."""
    data16 = value & BLOCK_MASK_16
    ptr16 = (value >> 16) & BLOCK_MASK_16
    return data16, ptr16

# ----------------------------
# Inicialização do disco
# ----------------------------
def init_disk():
    """Inicializa o disco e a lista livre."""
    global disk, free_head, free_size
    for i in range(NUM_BLOCKS):
        data = 0
        ptr = i + 1 if i + 1 < NUM_BLOCKS else NULL_PTR
        disk[i] = pack_block(data, ptr)
    free_head = 0
    free_size = NUM_BLOCKS
    directory.clear()
    print("[OK] Disco inicializado com sucesso.\n")

# ----------------------------
# Funções principais
# ----------------------------
def create_file(name: str, content: str) -> bool:
    """Cria um novo arquivo (palavra) no disco encadeado."""
    global free_head, free_size, directory, disk

    if len(name) == 0 or len(name) > 4:
        print(f"[ERRO] Nome '{name}' inválido. Use até 4 caracteres.")
        return False
    if name in directory:
        print(f"[ERRO] Arquivo '{name}' já existe.")
        return False

    needed = len(content)
    if needed == 0:
        print("[ERRO] Conteúdo vazio. Nada a armazenar.")
        return False
    if free_size < needed:
        print(f"[ERRO] Memória insuficiente ({free_size} blocos livres, precisa de {needed}).")
        return False

    allocated_indices: List[int] = []
    for _ in range(needed):
        if free_head is None or free_head == NULL_PTR:
            print("[ERRO] Lista livre vazia durante alocação.")
            for idx in allocated_indices:
                data, ptr = unpack_block(disk[idx])
                disk[idx] = pack_block(0, free_head if free_head is not None else NULL_PTR)
                free_head = idx
                free_size += 1
            return False

        idx = free_head
        _, next_free = unpack_block(disk[idx])
        free_head = next_free if next_free != NULL_PTR else None
        allocated_indices.append(idx)
        free_size -= 1

    for i, ch in enumerate(content):
        idx = allocated_indices[i]
        data16 = ord(ch)
        next_ptr = allocated_indices[i+1] if i + 1 < len(allocated_indices) else NULL_PTR
        disk[idx] = pack_block(data16, next_ptr)

    directory[name] = (allocated_indices[0], needed)
    print(f"[OK] Arquivo '{name}' criado. ({needed} blocos usados, início em {allocated_indices[0]})")
    return True

def read_file(name: str) -> Optional[str]:
    """Lê e exibe o conteúdo de um arquivo."""
    if name not in directory:
        print(f"[ERRO] Arquivo '{name}' não encontrado.")
        return None

    start_idx, _ = directory[name]
    content = ""
    idx = start_idx
    seen = set()
    while idx != NULL_PTR:
        if idx in seen:
            print("[ERRO] Loop detectado (corrupção).")
            break
        seen.add(idx)
        data16, ptr16 = unpack_block(disk[idx])
        content += chr(data16) if data16 != 0 else '?'
        idx = ptr16

    print(f"\n[LEITURA] {name}: \"{content}\"")
    return content

def delete_file(name: str) -> bool:
    """Exclui o arquivo e libera seus blocos."""
    global free_head, free_size, directory, disk
    if name not in directory:
        print(f"[ERRO] Arquivo '{name}' não existe.")
        return False

    start_idx, _ = directory[name]
    idx = start_idx
    seen = set()
    freed = 0

    while idx != NULL_PTR:
        if idx in seen:
            print("[ERRO] Loop detectado (corrupção).")
            break
        seen.add(idx)
        data16, ptr16 = unpack_block(disk[idx])
        next_idx = ptr16
        disk[idx] = pack_block(0, free_head if free_head is not None else NULL_PTR)
        free_head = idx
        free_size += 1
        freed += 1
        idx = next_idx

    del directory[name]
    print(f"[OK] Arquivo '{name}' excluído ({freed} blocos liberados).")
    return True

# ----------------------------
# Funções de exibição
# ----------------------------
def print_disk_detailed():
    print("\nDISCO DETALHADO:")
    print("Bloco | Dado | Char | Ponteiro")
    print("------------------------------")
    for i in range(NUM_BLOCKS):
        data16, ptr16 = unpack_block(disk[i])
        char = chr(data16) if (32 <= data16 <= 126) else '.'
        ptr = str(ptr16) if ptr16 != NULL_PTR else "NULL"
        print(f"{i:3}   | {data16:5} |  {char:^3}  | {ptr}")
    print("------------------------------")

def print_directory():
    print("\nTABELA DE DIRETÓRIO:")
    if not directory:
        print("  (vazia)")
        return
    print("Nome | Início | Tamanho")
    print("-----------------------")
    for name, (start, size) in directory.items():
        print(f"{name:4} | {start:6} | {size}")
    print("-----------------------")

def print_free_list():
    print("\nBLOCOS LIVRES:")
    if free_head is None:
        print("  (nenhum)")
        return
    seq = []
    idx = free_head
    seen = set()
    while idx != NULL_PTR and idx is not None:
        if idx in seen:
            seq.append(f"{idx}(loop?)")
            break
        seen.add(idx)
        seq.append(str(idx))
        _, ptr = unpack_block(disk[idx])
        idx = ptr if ptr != NULL_PTR else NULL_PTR
    print(" -> ".join(seq))
    print(f"Total livres: {free_size}\n")

# ----------------------------
# Interface de linha de comando
# ----------------------------
def menu():
    print("""
=============================
 SISTEMA DE ARQUIVOS (ENC.)
=============================
1 - Criar arquivo
2 - Ler arquivo
3 - Excluir arquivo
4 - Exibir tabela de diretório
5 - Exibir blocos livres
6 - Exibir disco detalhado
7 - Recriar disco (resetar tudo)
0 - Sair
=============================
""")

def interface():
    init_disk()
    while True:
        menu()
        opc = input("Escolha uma opção: ").strip()
        if opc == '1':
            nome = input("Nome do arquivo (até 4 chars): ").strip()
            conteudo = input("Conteúdo (texto): ")
            create_file(nome, conteudo)
        elif opc == '2':
            nome = input("Nome do arquivo a ler: ").strip()
            read_file(nome)
        elif opc == '3':
            nome = input("Nome do arquivo a excluir: ").strip()
            delete_file(nome)
        elif opc == '4':
            print_directory()
        elif opc == '5':
            print_free_list()
        elif opc == '6':
            print_disk_detailed()
        elif opc == '7':
            confirma = input("Tem certeza que deseja limpar o disco? (s/n): ").lower()
            if confirma == 's':
                init_disk()
        elif opc == '0':
            print("Encerrando o sistema...")
            break
        else:
            print("[ERRO] Opção inválida.")
        input("\nPressione ENTER para continuar...")

# ----------------------------
# Execução principal
# ----------------------------
if __name__ == "__main__":
    print("=== SISTEMA DE GERENCIAMENTO DE ARQUIVOS ENC. ===")
    escolha = input("Deseja rodar o modo demonstração (d) ou interativo (i)? [d/i]: ").lower()
    if escolha == 'd':
        from sys import exit
        # Executa o exemplo do enunciado
        def demo():
            init_disk()
            create_file("f1", "Pernambuco")
            create_file("f2", "Sao Paulo")
            create_file("f3", "Alagoas")
            create_file("f4", "Santa Catarina")  # falha esperada
            delete_file("f2")
            create_file("f4", "Santa Catarina")  # sucesso
            print_directory()
            print_disk_detailed()
            print_free_list()
        demo()
        exit(0)
    else:
        interface()
