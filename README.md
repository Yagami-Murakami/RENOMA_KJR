# Ferramenta de Mídia em Python

![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux%20%7C%20Android-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Um script interativo de linha de comando, escrito em Python, para automatizar tarefas de mídia. Ideal para organizar coleções de séries e converter arquivos de vídeo e áudio em lote com eficiência.

## Principais Funcionalidades

-   **Renomeador de Séries:** Renomeia arquivos de vídeo em sequência, seguindo o padrão `Nome da Série S01E01.ext`.
-   **Conversor de Vídeo:**
    -   Converte vídeos em lote para formatos como `.mp4` e `.mkv`.
    -   **Aceleração de Hardware:** Detecta e utiliza a placa de vídeo para conversões muito mais rápidas (NVIDIA, Intel, AMD no Windows; VA-API no Linux; MediaCodec no Android).
    -   Oferece opção de usar o processador (`libx264`) com presets de velocidade.
    -   Mantém as trilhas de áudio originais sem perda de qualidade.
-   **Conversor de Áudio:**
    -   Converte arquivos de áudio em lote.
    -   Inclui presets de alta qualidade para formatos modernos e compatíveis como **FLAC (lossless)**, **MP3 (320kbps)** e **AAC/M4A (VBR)**.
-   **Multiplataforma:** Projetado para funcionar em Windows, Linux e até mesmo em Android via Termux.
-   **Interface Amigável:** Guiado por menus interativos que facilitam o uso.

---

## Compatibilidade

O script foi testado e funciona nos seguintes sistemas operacionais:

| Plataforma                     | Suportado | Observações                               |
| ------------------------------ | :-------: | ----------------------------------------- |
| **Windows 10 / 11** |     ✅     | Suporta aceleração via NVIDIA, Intel, AMD |
| **Linux (Debian, Ubuntu, etc)**|     ✅     | Suporta aceleração via VA-API             |
| **Android (via Termux)** |     ✅     | Suporta aceleração via MediaCodec         |

---

## Pré-requisitos

Antes de executar o script, você precisa ter dois programas instalados em seu sistema:

1.  **Python 3:** Versão 3.7 ou mais recente.
2.  **FFmpeg:** A ferramenta que faz todo o trabalho pesado de conversão.

## Instalação

Siga os passos abaixo para preparar seu ambiente.

### 1. Obtenha o Código
Clone este repositório para a sua máquina local:
```bash
git clone https://github.com/Yagami-Murakami/RENOMA_KJR.git
cd RENOMA_KJR

2. Instale as Dependências Python
O script precisa da biblioteca tqdm para exibir as barras de progresso. Instale-a com o pip:

pip install tqdm

3. Instale o FFmpeg

No Windows
O jeito mais fácil é usar o gerenciador de pacotes Winget. Abra o Prompt de Comando ou PowerShell e rode:

winget install ffmpeg

No Linux (Debian/Ubuntu)
Use o gerenciador de pacotes apt. Abra o terminal e rode:

sudo apt update && sudo apt install ffmpeg

No Android (Termux)
Use o gerenciador de pacotes pkg. Abra o Termux e rode:

pkg update && pkg install ffmpeg python

Como Usar
Coloque o script na pasta correta: Mova o arquivo .py para dentro da pasta onde estão os arquivos de mídia que você deseja processar.

Abra um terminal nessa pasta:

Windows: Navegue até a pasta pelo Explorador de Arquivos, clique na barra de endereço, digite cmd e pressione Enter.

Linux: Navegue até a pasta pelo seu gerenciador de arquivos, clique com o botão direito e selecione "Abrir no terminal".

Android (Termux): Use o comando cd para navegar, por exemplo: cd storage/downloads/MinhaSerie.

Execute o script:


python renoma.py
(Substitua renoma.py pelo nome real do arquivo no seu repositório).

Siga o menu: O script irá exibir um menu interativo. Basta escolher a opção desejada (renomear, converter vídeo ou áudio) e seguir as instruções na tela.



