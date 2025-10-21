# Sistema de Gerenciamento de Arquivos Usando Lista Encadeada

**Universidade Federal de Alagoas (UFAL) — Campus Arapiraca – SEDE**  
**Curso:** Bacharelado em Ciência da Computação  
**Disciplina:** Sistemas Operacionais  
**Caixa Postal:** 57309-005 – Arapiraca – AL – Brasil  

**Docente: Tércio Moraes**

**Alunos:**  
1. [Jhony Wictor do Nascimento Santos – 23112167](https://github.com/jhonywsantos)
2. [Lucas Rosendo de Farias – 23112728](https://github.com/LucaRosendo)
3. [Washington Medeiros Mazzone Gaia – 23112555](https://github.com/washingmg)  

**E-mails:** {jhony.santos, karleandro.silva, lucas.farias, washington.gaia}@arapiraca.ufal.br  

---

## 🧩 Resumo

Este trabalho apresenta a implementação de um **sistema de gerenciamento de arquivos baseado em lista encadeada**, utilizando a linguagem **Python** para simular o funcionamento de um disco e suas operações de alocação de blocos. A proposta busca reproduzir conceitos fundamentais de **gerenciamento de memória secundária**, como alocação dinâmica, controle de espaço livre e encadeamento de blocos. Cada arquivo é dividido em blocos de dados interligados por ponteiros, simulando a estrutura física de um disco rígido. O sistema permite a criação, leitura e exclusão de arquivos, bem como a visualização do estado do disco, da tabela de diretório e da memória livre, de forma interativa via linha de comando.

_**Palavras-chaves: gerenciamento de memória secundária, alocação dinâmica, controle de espaço**_

---

## 🧠 Abstract

_This work presents the implementation of a **linked-list-based file management system** using **Python** to simulate the operation of a disk and its block allocation mechanisms. The system reproduces essential concepts of **secondary memory management**, such as dynamic allocation, free space control, and block chaining. Each file is divided into data blocks connected by pointers, simulating the physical structure of a hard disk. The program allows users to create, read, and delete files, as well as visualize the state of the disk, directory table, and free memory through an interactive command-line interface._

_**Keywords: secondary memory management, dynamic allocation, space control**_

---

## 📘 Introdução

Nos sistemas operacionais, o **gerenciamento de arquivos** é uma das tarefas mais importantes, pois permite armazenar, acessar e manipular informações em memória secundária. Uma das técnicas clássicas para realizar essa tarefa é a **alocação encadeada**, na qual cada arquivo é dividido em blocos conectados entre si por ponteiros.  

Neste trabalho, desenvolveu-se uma **simulação de sistema de arquivos com lista encadeada**, utilizando arrays para representar os blocos de um disco de 1024 bits, divididos em 32 blocos de 32 bits cada. Cada bloco armazena 16 bits de dados (caractere) e 16 bits de ponteiro (inteiro curto), simulando a estrutura real de armazenamento em baixo nível.  

O sistema permite a **criação, leitura e exclusão de arquivos**, além de manter uma **tabela de diretório** e um **gerenciador de memória livre**, garantindo que arquivos possam ser alocados mesmo quando os espaços disponíveis não são contíguos.

---

## ⚙️ Desenvolvimento

A implementação foi realizada em **Python**, utilizando o módulo `array` para representar o disco de forma fiel às restrições do problema.  

O código foi estruturado em componentes principais:

### 1. Estrutura do Disco
O disco é representado por um array de 32 posições. Cada posição contém duas informações:
- Um caractere de dado (`char`).
- Um ponteiro (`int`) indicando o próximo bloco.

O último bloco de cada arquivo contém um ponteiro nulo (`-1`), indicando o final do arquivo.

### 2. Tabela de Diretório
A tabela de diretório armazena o **nome do arquivo** e o **índice do primeiro bloco**. Essa estrutura é fundamental para localizar o início do encadeamento e realizar operações como leitura ou exclusão.

### 3. Gerenciamento da Memória Livre
A lista encadeada de blocos livres é mantida por meio de ponteiros que conectam os blocos não utilizados.  
Ao criar um novo arquivo, o sistema verifica se há **blocos livres suficientes**, mesmo que fragmentados, para armazenar todos os caracteres.  
Se não houver espaço suficiente, é exibida uma mensagem de **“Memória insuficiente”**.

### 4. Operações Principais

- **Criação de arquivo:** o usuário insere um nome e o conteúdo. O sistema aloca blocos disponíveis e atualiza o diretório.  
- **Leitura de arquivo:** percorre os blocos encadeados exibindo o conteúdo do arquivo na tela.  
- **Exclusão de arquivo:** libera os blocos utilizados, reconectando-os à lista de blocos livres.  
- **Visualização:** mostra o estado atual do disco, tabela de diretório e blocos disponíveis.

### 5. Interface Interativa
O sistema oferece uma **interface simples de linha de comando (CLI)**, onde o usuário pode escolher entre:
- Criar arquivo  
- Ler arquivo  
- Excluir arquivo  
- Visualizar disco e diretório  
- Encerrar o programa  

Essa interface foi projetada para demonstrar de forma didática o funcionamento do sistema de arquivos encadeado.

---

## 🧪 Exemplo de Execução

Durante a execução, o programa segue o comportamento ilustrado na figura apresentada no enunciado:

1. São criados os arquivos:  
   - `Pernambuco`  
   - `Sao Paulo`  
   - `Alagoas`  

2. Ao tentar adicionar “Santa Catarina”, o sistema informa **memória insuficiente**.

3. Após excluir “Sao Paulo”, é possível adicionar “Santa Catarina” com sucesso, utilizando os blocos que ficaram livres.

O processo demonstra claramente a **reutilização de blocos livres não contíguos** e o comportamento dinâmico da **lista encadeada**.

---

## 🧾 Conclusão

O trabalho possibilitou compreender, de forma prática, como ocorre o **gerenciamento de arquivos e blocos de memória em sistemas operacionais**. A simulação com listas encadeadas mostrou-se eficiente para representar a alocação dinâmica e a fragmentação do espaço livre, conceitos essenciais para o funcionamento de sistemas reais de armazenamento.  

Além de consolidar o aprendizado sobre estruturas de dados e manipulação de memória, o projeto reforçou o entendimento de **como sistemas operacionais controlam o uso do disco**, recuperando blocos e reorganizando dados sem perda de integridade.  

A implementação proposta cumpre os objetivos didáticos, demonstrando com clareza o processo de criação, leitura e exclusão de arquivos em um ambiente controlado e interativo.

---

## 💻 Execução

Para executar o programa:

```bash
python sistema_arquivos_encadeado.py
