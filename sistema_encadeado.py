"""
sistema_arquivos_encadeado.py

Simulação de gerenciamento de arquivos usando lista encadeada em disco.
Cada bloco do disco tem 32 bits:
 - 16 bits para DADOS (um caractere: armazenamos ord(c) em 0..65535)
 - 16 bits para PONTEIRO (índice do próximo bloco, ou NULL_PTR)
O "disco" é um array de 32 blocos (32 * 32 bits = 1024 bits).

Implementa:
 - criar arquivo (palavra) com nome (até 4 chars)
 - ler arquivo (mostrar conteúdo)
 - excluir arquivo (liberar blocos e encadeá-los na lista livre)
 - funções auxiliares de impressão (disco, diretório, índices livres)
"""

from array import array
from typing import Dict, Optional, List, Tuple

# ----------------------------
# Configurações / constantes
# ----------------------------
NUM_BLOCKS = 32            # número de blocos no disco (32 * 32 bits = 1024 bits)
NULL_PTR = 0xFFFF          # valor 16-bit usado para ponteiro nulo (65535)
BLOCK_MASK_16 = 0xFFFF     # máscara para 16 bits
TYPECODE = 'I'             # 32-bit unsigned para representar cada bloco (16+16 bits)

# ----------------------------
# Estruturas globais (simulação)
# ----------------------------
disk = array(TYPECODE, [0] * NUM_BLOCKS)
# tabela de diretório: mapeia nome (str) -> (start_index:int, length:int)
directory: Dict[str, Tuple[int, int]] = {}
# ponteiro para início da lista de blocos livres
free_head: Optional[int] = None
# contagem de blocos livres disponíveis
free_size: int = 0

# ----------------------------
# Funções utilitárias de empacotamento
# ----------------------------
def pack_block(data16: int, ptr16: int) -> int:
    """
    Empacota data16 (16-bit) e ptr16 (16-bit) em um inteiro 32-bit:
    formato: [ptr16 (alta 16 bits)] [data16 (baixa 16 bits)]
    """
    return ((ptr16 & BLOCK_MASK_16) << 16) | (data16 & BLOCK_MASK_16)

def unpack_block(value: int) -> Tuple[int, int]:
    """
    Desempacota o inteiro 32-bit em (data16, ptr16).
    Retorna (data16, ptr16).
    """
    data16 = value & BLOCK_MASK_16
    ptr16 = (value >> 16) & BLOCK_MASK_16
    return data16, ptr16

# ----------------------------
# Inicialização do disco
# ----------------------------
def init_disk():
    """
    Inicializa o disco vazio:
    - cada bloco aponta para o próximo (0 -> 1 -> 2 -> ... -> 31 -> NULL)
    - dados = 0 em todos
    - free_head = 0, free_size = NUM_BLOCKS
    """
    global disk, free_head, free_size
    for i in range(NUM_BLOCKS):
        data = 0
        ptr = i + 1 if i + 1 < NUM_BLOCKS else NULL_PTR
        disk[i] = pack_block(data, ptr)
    free_head = 0
    free_size = NUM_BLOCKS

# ----------------------------
# Funções principais
# ----------------------------
def create_file(name: str, content: str) -> bool:
    """
    Cria um "arquivo" com nome (<=4 chars) e conteúdo (string).
    Verifica se há espaço livre total suficiente (mesmo que não contíguo).
    Se houver, aloca blocos, armazena cada caractere em um bloco e
    encadeia os blocos no disco. Atualiza a tabela de diretório.
    Retorna True se sucesso, False caso espaço insuficiente ou nome inválido.
    """
    global free_head, free_size, directory, disk

    # validações
    if len(name) == 0 or len(name) > 4:
        print(f"[ERRO] Nome '{name}' inválido: deve ter 1 a 4 caracteres.")
        return False
    if name in directory:
        print(f"[ERRO] Nome '{name}' já existe na tabela de diretório.")
        return False

    needed = len(content)
    if needed == 0:
        print("[AVISO] Conteúdo vazio — nada a armazenar. Criação ignorada.")
        return False

    # verifica se há blocos livres suficientes (contagem total)
    if free_size < needed:
        print(f"[ERRO] Memória insuficiente: precisa {needed} blocos, disponíveis {free_size}.")
        return False

    # alocar blocos: retirar do início da lista livre
    allocated_indices: List[int] = []
    for _ in range(needed):
        if free_head is None or free_head == NULL_PTR:
            # não deveria ocorrer pois checamos free_size, mas checagem defensiva
            print("[ERRO] Lista livre inesperadamente vazia durante alocação.")
            # desfazer alocações já feitas
            for idx in allocated_indices:
                # recolocar na lista livre
                data, ptr = unpack_block(disk[idx])
                disk[idx] = pack_block(0, free_head if free_head is not None else NULL_PTR)
                free_head = idx
                free_size += 1
            return False

        idx = free_head
        _, next_free = unpack_block(disk[idx])  # next_free é o ponteiro para o próximo bloco livre
        # remove idx da lista livre ajustando free_head
        free_head = next_free if next_free != NULL_PTR else None
        allocated_indices.append(idx)
        free_size -= 1

    # agora gravar os dados nos blocos alocados e encadeá-los
    for i, ch in enumerate(content):
        idx = allocated_indices[i]
        data16 = ord(ch)  # codifica caractere como inteiro 0..65535
        # ponteiro para o próximo bloco alocado, ou NULL_PTR se for último
        next_ptr = allocated_indices[i+1] if i + 1 < len(allocated_indices) else NULL_PTR
        disk[idx] = pack_block(data16, next_ptr)

    # atualizar diretório com (start_index, length)
    directory[name] = (allocated_indices[0], needed)
    print(f"[OK] Arquivo '{name}' criado, começa no bloco {allocated_indices[0]}, tamanho {needed}.")
    return True

def read_file(name: str) -> Optional[str]:
    """
    Lê o arquivo com nome 'name' e retorna o conteúdo (string).
    Se o arquivo não existir, retorna None.
    """
    if name not in directory:
        print(f"[ERRO] Arquivo '{name}' não encontrado no diretório.")
        return None

    start_idx, _ = directory[name]
    chars: List[str] = []
    idx = start_idx
    seen = set()  # prevenção contra loops acidentais
    while idx != NULL_PTR:
        if idx in seen:
            print("[ERRO] Loop detectado na cadeia de blocos do arquivo (corrupção).")
            break
        seen.add(idx)
        data16, ptr16 = unpack_block(disk[idx])
        if data16 == 0:
            # bloco vazio — comportamento possível mas indicaria problema
            chars.append('?')
        else:
            try:
                chars.append(chr(data16))
            except ValueError:
                chars.append('?')
        idx = ptr16
    content = ''.join(chars)
    print(f"[LEITURA] Arquivo '{name}': \"{content}\"")
    return content

def delete_file(name: str) -> bool:
    """
    Exclui o arquivo 'name' liberando seus blocos e encadeando-os no início da lista livre.
    Retorna True se excluído com sucesso, False se arquivo não existir.
    """
    global free_head, free_size, directory, disk

    if name not in directory:
        print(f"[ERRO] Arquivo '{name}' não encontrado para exclusão.")
        return False

    start_idx, _ = directory[name]
    idx = start_idx
    seen = set()
    freed_count = 0
    while idx != NULL_PTR:
        if idx in seen:
            print("[ERRO] Loop detectado durante exclusão (corrupção).")
            break
        seen.add(idx)
        data16, ptr16 = unpack_block(disk[idx])
        next_idx = ptr16  # onde o arquivo aponta para seguir
        # limpar dados e inserir esse bloco no início da lista livre
        disk[idx] = pack_block(0, free_head if free_head is not None else NULL_PTR)
        free_head = idx
        free_size += 1
        freed_count += 1
        idx = next_idx

    # remover do diretório
    del directory[name]
    print(f"[OK] Arquivo '{name}' excluído. {freed_count} blocos liberados.")
    return True

# ----------------------------
# Funções de impressão / exibição
# ----------------------------
def print_disk_detailed():
    """
    Imprime cada bloco do disco com índice, dado (caractere se imprimível) e ponteiro.
    """
    print("\nDISCO (detalhado):")
    print("Índ | Dado (ord) | Caractere | Ponteiro")
    print("--------------------------------------")
    for i in range(NUM_BLOCKS):
        data16, ptr16 = unpack_block(disk[i])
        ch = chr(data16) if (data16 != 0 and 32 <= data16 <= 126) else ('.' if data16 != 0 else '-')
        ptr_str = str(ptr16) if ptr16 != NULL_PTR else 'NULL'
        print(f"{i:3} | {data16:9} |    {ch:^3}   | {ptr_str}")
    print("--------------------------------------")

def print_directory():
    """
    Imprime a tabela de diretório com nome, bloco inicial e tamanho.
    """
    print("\nTABELA DE DIRETÓRIO:")
    if not directory:
        print(" <vazia>")
        return
    print("Nome | Início | Tamanho")
    print("-----------------------")
    for name, (start, length) in directory.items():
        print(f"{name:4} | {start:6} | {length}")
    print("-----------------------")

def print_free_list():
    """
    Imprime os índices dos blocos livres seguindo a lista livre.
    """
    print("\nBLOCOS LIVRES (lista encadeada):")
    if free_head is None:
        print(" <nenhum>")
        return
    idx = free_head
    seq = []
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
    print(f"Total blocos livres (free_size): {free_size}")

def print_file(name: str):
    """
    Mostra o conteúdo do arquivo (usando read_file).
    """
    content = read_file(name)
    if content is not None:
        print(f"Conteúdo de '{name}': {content}")

# ----------------------------
# Demonstração (exemplo do enunciado)
# ----------------------------
def demo_enunciado():
    """
    Executa as operações descritas no enunciado:
    - inicia disco vazio
    - adiciona f1=Pernambuco, f2='Sao Paulo', f3=Alagoas
    - tenta adicionar f4='Santa Catarina' (deve falhar por falta de espaço)
    - exclui f2
    - tenta adicionar f4 novamente (deve agora ter sucesso)
    """
    print("=== DEMONSTRAÇÃO: gerenciador de arquivos encadeado ===")
    init_disk()
    print_disk_detailed()
    print_free_list()
    print_directory()

    # cadastrar arquivos do exemplo
    create_file("f1", "Pernambuco")   # 10 chars
    create_file("f2", "Sao Paulo")    # 9 chars (inclui espaço)
    create_file("f3", "Alagoas")      # 7 chars

    print_directory()
    print_disk_detailed()
    print_free_list()

    # tentativa que deve falhar: Santa Catarina (14 chars)
    print("\nTentativa de inserir f4='Santa Catarina' (deve falhar):")
    ok = create_file("f4", "Santa Catarina")
    if not ok:
        print("Inserção f4 falhou conforme esperado (espaço insuficiente).")

    # excluir f2
    print("\nExcluindo f2 ('Sao Paulo'):")
    delete_file("f2")
    print_directory()
    print_free_list()

    # nova tentativa: agora deve caber
    print("\nTentativa de inserir f4='Santa Catarina' novamente (deve ter sucesso):")
    ok2 = create_file("f4", "Santa Catarina")
    if ok2:
        print("Inserção f4 bem sucedida após liberação de espaço.")
    print_directory()
    print_disk_detailed()
    print_free_list()

    # leitura de arquivos para demonstrar leitura funcional
    print("\nLeituras de arquivos atuais:")
    for name in list(directory.keys()):
        print_file(name)

# ----------------------------
# Execução principal
# ----------------------------
if __name__ == "__main__":
    # Roda a demonstração completa automaticamente
    demo_enunciado()
