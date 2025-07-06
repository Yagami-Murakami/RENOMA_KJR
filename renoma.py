#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#################################################################
#  Ferramenta interativa para:                                  #
#    • Renomear episódios de séries                             #
#    • Converter vídeos em lote (HW-Accel/CPU)                  #
#    • Converter áudios em lote (com presets de qualidade)      #
#  – Versão com conversor de ÁUDIO integrado                    #
#################################################################

import os
import sys
import re
import glob
import shutil
import time
import subprocess
import platform
from pathlib import Path
from tqdm import tqdm

# ────────────────────────── Configurações ──────────────────────────
BANNER_COLORS = [
    '\033[0;31m', '\033[1;31m', '\033[0;32m', '\033[1;32m',
    '\033[0;34m', '\033[1;34m', '\033[0;35m', '\033[1;35m',
    '\033[0;36m', '\033[1;36m', '\033[1;33m'
]
NUM_BANNER_COLORS = len(BANNER_COLORS)
NC = '\033[0m'
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_ANDROID = 'com.termux' in os.environ.get('PREFIX', '')

FFMPEG = shutil.which("ffmpeg") or ("ffmpeg.exe" if IS_WINDOWS else "/usr/bin/ffmpeg")
FFPROBE = shutil.which("ffprobe") or ("ffprobe.exe" if IS_WINDOWS else "/usr/bin/ffprobe")
VAAPI_DEVICE = "/dev/dri/renderD128"
WATCHDOG_TIMEOUT = 120

# ... (As funções print_art, clear_screen, get_duration e run_rename_logic não mudaram) ...
def print_art(current_color_index=0):
    """Função para imprimir a arte ASCII"""
    safe_index = current_color_index % (NUM_BANNER_COLORS if NUM_BANNER_COLORS > 0 else 1)
    color = BANNER_COLORS[safe_index]
    
    print(f"{color}")
    ascii_art = """



██████╗░███████╗███╗░░██╗░█████╗░███╗░░░███╗░█████╗░
██╔══██╗██╔════╝████╗░██║██╔══██╗████╗░████║██╔══██╗
██████╔╝█████╗░░██╔██╗██║██║░░██║██╔████╔██║███████║
██╔══██╗██╔══╝░░██║╚████║██║░░██║██║╚██╔╝██║██╔══██║
██║░░██║███████╗██║░╚███║╚█████╔╝██║░╚═╝░██║██║░░██║
╚═╝░░╚═╝╚══════╝╚═╝░░╚══╝░╚════╝░╚═╝░░░░░╚═╝╚═╝░░╚═╝

██╗░░██╗░░░░░██╗██████╗░
██║░██╔╝░░░░░██║██╔══██╗
█████═╝░░░░░░██║██████╔╝
██╔═██╗░██╗░░██║██╔══██╗
██║░╚██╗╚█████╔╝██║░░██║
╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""
    
    print(ascii_art)
    print(f"{NC}")
    print()

def clear_screen():
    """Limpa a tela de forma multiplataforma"""
    os.system('cls' if IS_WINDOWS else 'clear')

def get_duration(file_path):
    """Obtém a duração de um arquivo de mídia em segundos"""
    try:
        result = subprocess.check_output([
            FFPROBE, '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', file_path
        ], text=True, stderr=subprocess.DEVNULL)
        return float(result.strip())
    except Exception:
        print(f"  ⚠️  Não foi possível obter a duração de {file_path}. Usando valor padrão.")
        return 1.0

def run_rename_logic():
    """Função de renomear arquivos sequencialmente"""
    print()
    print("===========================================")
    print("=== Modo: Renomear Arquivos Sequencialmente ===")
    print("===========================================")
    print()
    
    while True:
        nome_serie = input(">> Digite o NOME da série (ex: The Mandalorian): ").strip()
        if nome_serie:
            break
        print("   ERRO: O nome da série não pode ficar em branco. Tente novamente.")
    
    print()
    
    while True:
        numero_temporada = input(">> Digite o NÚMERO da temporada (ex: 5): ").strip()
        if re.match(r'^[1-9][0-9]*$', numero_temporada):
            break
        print("   ERRO: Por favor, digite um número inteiro positivo para a temporada.")
    
    temporada_formatada = f"{int(numero_temporada):02d}"
    print()
    
    print(">> Escolha o TIPO de arquivo a ser renomeado:")
    print("   1) .mp4")
    print("   2) .mkv")
    print("   3) .avi")
    
    while True:
        escolha_ext = input("   Digite o número da opção (1, 2 ou 3): ").strip()
        if escolha_ext in ["1", "2", "3"]:
            extensao = {"1": "mp4", "2": "mkv", "3": "avi"}[escolha_ext]
            break
        else:
            print("   ERRO: Opção inválida. Por favor, digite 1, 2 ou 3.")
    
    print()
    
    print("=======================================================")
    print("=== Resumo da Configuração (Renomear) ===")
    print(f"Série:           '{nome_serie}'")
    print(f"Temporada:       {temporada_formatada}")
    print(f"Tipo de Arquivo: '.{extensao}'")
    print(f"Pasta Alvo:      '{SCRIPT_DIR}'")
    print(f"Novo Formato:    {nome_serie} S{temporada_formatada}EXX.{extensao}")
    print("=======================================================")
    print()
    
    print(f">> Procurando arquivos *.{extensao} neste diretório...")
    print(">> Os arquivos serão numerados sequencialmente (E01, E02...) baseado na ordem alfabética atual.")
    print("-----------------------------------------------------")
    print(">> IMPORTANTE: Verifique se a ordem de renomeação abaixo está correta ANTES de confirmar!")
    print(">> Pressione ENTER para listar os arquivos e as mudanças propostas, ou CTRL+C para cancelar.")
    
    try:
        input("")
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        return
    
    arquivos = sorted(glob.glob(f"*.{extensao}"))
    script_name = os.path.basename(__file__)
    
    renames = {}
    arquivos_listados = 0
    episode_counter = 1
    
    for arquivo_antigo in arquivos:
        if arquivo_antigo == script_name:
            continue
        
        episodio_formatado = f"{episode_counter:02d}"
        novo_nome = f"{nome_serie} S{temporada_formatada}E{episodio_formatado}.{extensao}"
        
        if arquivo_antigo != novo_nome:
            print(f"  '{arquivo_antigo}'  ==>  '{novo_nome}'")
            renames[arquivo_antigo] = novo_nome
            arquivos_listados += 1
        else:
            print(f"  '{arquivo_antigo}'  (já está no formato ou nome igual, será ignorado)")
        
        episode_counter += 1
    
    print("-----------------------------------------------------")
    
    if arquivos_listados == 0:
        print(f"Nenhum arquivo *.{extensao} encontrado para renomear ou todos já estão no formato correto.")
        return
    
    print(f">> Foram propostas {arquivos_listados} renomeações.")
    confirmacao = input(">> Você confirma que a ordem acima está correta e deseja renomear os arquivos? (s/N): ").strip()
    print()
    
    if confirmacao.lower() == 's':
        print(">> Renomeando arquivos...")
        arquivos_renomeados = 0
        erros = 0
        
        for arquivo_antigo, novo_nome in renames.items():
            try:
                if not os.path.exists(novo_nome):
                    os.rename(arquivo_antigo, novo_nome)
                    print(f"  OK: '{arquivo_antigo}' -> '{novo_nome}'")
                    arquivos_renomeados += 1
                else:
                    print(f"  ERRO: Arquivo '{novo_nome}' já existe")
                    erros += 1
            except Exception as e:
                print(f"  ERRO ao tentar renomear '{arquivo_antigo}' para '{novo_nome}': {e}")
                erros += 1
        
        print("-----------------------------------------------------")
        print(">> Renomeação concluída.")
        print(f"- Arquivos renomeados com sucesso: {arquivos_renomeados}")
        if erros > 0:
            print(f"- Erros encontrados: {erros}")
    else:
        print(">> Renomeação cancelada pelo usuário.")

# ─────────────────── Lógica de Conversão de VÍDEO ───────────────────
def get_available_encoders():
    preset_cpu = "veryfast" if IS_ANDROID else "medium"
    encoders = { 'cpu': {'name': f'CPU (libx264 - preset {preset_cpu})', 'codec': 'libx264', 'preset': preset_cpu} }
    if IS_ANDROID:
        encoders['mediacodec'] = {'name': 'Android Hardware (h264_mediacodec)', 'codec': 'h264_mediacodec'}
    if IS_WINDOWS:
        try:
            result = subprocess.check_output("wmic path win32_videocontroller get name", shell=True, text=True, stderr=subprocess.DEVNULL).lower()
            if 'intel' in result: encoders['qsv'] = {'name': 'Intel Quick Sync (h264_qsv)', 'codec': 'h264_qsv'}
            if 'nvidia' in result: encoders['nvenc'] = {'name': 'NVIDIA NVENC (h264_nvenc)', 'codec': 'h264_nvenc'}
            if 'amd' in result or 'radeon' in result: encoders['amf'] = {'name': 'AMD AMF (h264_amf)', 'codec': 'h264_amf'}
        except Exception: pass
    elif IS_LINUX and not IS_ANDROID:
        if Path(VAAPI_DEVICE).exists(): encoders['vaapi'] = {'name': 'Linux VA-API (h264_vaapi)', 'codec': 'h264_vaapi'}
    return encoders

def convert_one_video(src: Path, out_ext: str, encoder_info: dict, quality_preset: int) -> bool:
    dst = src.with_suffix(f".{out_ext}")
    encoder = encoder_info['codec']
    quality_map = {
        'libx264': {1: 19, 2: 23, 3: 28}, 'h264_qsv': {1: 20, 2: 26, 3: 32},
        'h264_nvenc': {1: 20, 2: 26, 3: 32}, 'h264_vaapi': {1: 20, 2: 26, 3: 32},
        'h264_amf': {1: 20, 2: 26, 3: 32}, 'h264_mediacodec': {1: '4M', 2: '2M', 3: '1M'}
    }
    quality_value = quality_map.get(encoder, {}).get(quality_preset, 23)
    vcodec_params = []
    if encoder == 'libx264': vcodec_params.extend(["-c:v", "libx264", "-crf", str(quality_value), "-preset", encoder_info.get('preset', 'medium')])
    elif encoder == 'h264_qsv': vcodec_params.extend(["-c:v", "h264_qsv", "-global_quality", str(quality_value), "-preset", "medium"])
    elif encoder == 'h264_nvenc': vcodec_params.extend(["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", str(quality_value)])
    elif encoder == 'h264_amf': vcodec_params.extend(["-c:v", "h264_amf", "-qp_i", str(quality_value), "-qp_p", str(quality_value), "-quality", "balanced"])
    elif encoder == 'h264_vaapi': vcodec_params.extend(["-vaapi_device", VAAPI_DEVICE, "-c:v", "h264_vaapi", "-vf", "format=nv12,hwupload", "-qp", str(quality_value)])
    elif encoder == 'h264_mediacodec': vcodec_params.extend(["-c:v", "h264_mediacodec", "-b:v", str(quality_value)])
    cmd = [ FFMPEG, "-nostdin", "-y", "-i", str(src), "-map", "0:v:0?", "-map", "0:a:0?", *vcodec_params, "-c:a", "copy", "-progress", "pipe:1", str(dst) ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, bufsize=1, encoding='utf-8', errors='replace')
    dur = get_duration(str(src)); last_update = time.time()
    bar = tqdm(total=100, desc=f"Convertendo {src.name} ({encoder_info.get('name', encoder)})", ncols=80, unit="%")
    try:
        for line in proc.stdout:
            if "out_time_ms=" in line:
                try:
                    t = int(line.strip().split("=")[1]) / 1_000_000; pct = min(int(t * 100 / dur), 100)
                    bar.n = pct; bar.refresh(); last_update = time.time()
                except (ValueError, IndexError): continue
            if time.time() - last_update > WATCHDOG_TIMEOUT:
                bar.write(f"⚠️  Sem progresso por {WATCHDOG_TIMEOUT}s. Abortando..."); proc.kill(); break
        bar.n = 100; bar.refresh(); proc.wait()
    finally: bar.close()
    if proc.returncode == 0 and dst.exists() and dst.stat().st_size > 1024: print("✅ Conversão de vídeo concluída!"); return True
    print(f"❌ Erro na conversão de vídeo (código: {proc.returncode})."); dst.unlink(missing_ok=True); return False

def run_video_convert_logic():
    platform_name = "Android" if IS_ANDROID else ("Windows" if IS_WINDOWS else "Linux")
    print("\n==========================================================")
    print(f"=== Modo: Converter Arquivos de VÍDEO ({platform_name}) ===")
    print("==========================================================")
    available_encoders = get_available_encoders()
    if len(available_encoders) > 1:
        print(">> Escolha o Codificador de Vídeo (Placa de Vídeo/CPU):")
        options = sorted(available_encoders.keys(), key=lambda x: (x != 'mediacodec', x != 'cpu'))
        for i, key in enumerate(options): print(f"   {i+1}) {available_encoders[key]['name']}")
        while True:
            try:
                choice = int(input(f"   Digite a opção (1-{len(options)}): ").strip())
                if 1 <= choice <= len(options):
                    chosen_encoder_key = options[choice - 1]; encoder_info = available_encoders[chosen_encoder_key]
                    print(f"   -> Usando: {encoder_info['name']}"); break
                else: print("   ERRO: Opção inválida.")
            except ValueError: print("   ERRO: Digite um número.")
    else:
        chosen_encoder_key = list(available_encoders.keys())[0]; encoder_info = available_encoders[chosen_encoder_key]
        print(f">> Apenas um codificador disponível. Usando: {encoder_info['name']}")
    print("\n>> Escolha o formato de ENTRADA (origem):")
    print("   1) .mkv\n   2) .avi\n   3) .mp4")
    while True:
        input_choice = input("   Opção ENTRADA (1-3): ").strip()
        if input_choice in ["1", "2", "3"]: input_ext = {"1": "mkv", "2": "avi", "3": "mp4"}[input_choice]; break
        else: print("   ERRO: Opção inválida.")
    print(">> Escolha o formato de SAÍDA (destino):")
    print("   1) .mp4\n   2) .mkv")
    while True:
        output_choice = input("   Opção SAÍDA (1-2): ").strip()
        if output_choice in ["1", "2"]: output_ext = {"1": "mp4", "2": "mkv"}[output_choice]; break
        else: print("   ERRO: Opção inválida.")
    if input_ext == output_ext: print("\nERRO: O formato de entrada e saída não podem ser iguais."); return
    print("\n>> Escolha a Qualidade de VÍDEO da Conversão:")
    print("   1) Alta\n   2) Média [Padrão]\n   3) Baixa")
    quality_preset = 2; quality_choice = input("   Digite a opção de Qualidade (1, 2 ou 3): ").strip()
    if quality_choice in ["1", "2", "3"]: quality_preset = int(quality_choice)
    else: print("   Opção inválida, usando qualidade Média (2).")
    print("\n>> Após uma conversão bem-sucedida, como lidar com o arquivo original?")
    print("   1) Deletar AUTOMATICAMENTE\n   2) PERGUNTAR antes de deletar [Padrão]")
    delete_mode = "2"; delete_choice = input("   Digite a opção de deleção (1 ou 2): ").strip()
    if delete_choice == "1": delete_mode = "1"
    if not os.path.isfile(FFMPEG) or not os.path.isfile(FFPROBE): print("ERRO: FFmpeg ou FFprobe não encontrado."); return
    input_files = sorted(Path(".").glob(f"*.{input_ext}"))
    if not input_files: print(f"Nenhum arquivo .{input_ext} encontrado."); return
    print(f"\nArquivos .{input_ext} encontrados ({len(input_files)}):")
    for file in input_files: print(f"  {file.name}")
    print("-----------------------------------------------------")
    confirm_batch = input(f">> Confirma a conversão de {len(input_files)} arquivos? (s/N): ").strip()
    if confirm_batch.lower() != 's': print("Conversão cancelada."); return
    converted_count, error_count, removed_count, failed_files = 0, 0, 0, []
    for i, input_file in enumerate(input_files):
        if input_file.name == os.path.basename(__file__): continue
        print(f"\n--- [{i+1}/{len(input_files)}] Processando: '{input_file.name}' ---")
        if convert_one_video(input_file, output_ext, encoder_info, quality_preset):
            converted_count += 1
            should_remove = False
            if delete_mode == "1": should_remove = True
            else:
                confirm_rm = input(f"    Remover o original '{input_file.name}'? (s/N): ").strip()
                if confirm_rm.lower() == 's': should_remove = True
            if should_remove:
                try: input_file.unlink(); print(f"     -> Original '{input_file.name}' removido."); removed_count += 1
                except Exception as e: print(f"     -> ERRO ao remover original: {e}"); error_count += 1
            else: print("     -> Original NÃO removido.")
        else: error_count += 1; failed_files.append(input_file.name)
        print("-----------------------------------------------------")
    print("\n======================================================")
    print(f">> Processamento de VÍDEO Concluído.")
    print(f"- Arquivos convertidos: {converted_count}\n- Originais removidos: {removed_count}\n- Erros: {error_count}")
    if failed_files:
        print(f"- Arquivos que falharam:"); [print(f"  • {f}") for f in failed_files]
    print("======================================================")

# ─────────────────── Lógica de Conversão de ÁUDIO ───────────────────
def convert_one_audio(src: Path, preset_info: dict) -> bool:
    """Converte um único arquivo de áudio usando o preset selecionado."""
    dst = src.with_suffix(f".{preset_info['ext']}")
    if src.resolve() == dst.resolve():
        print(f"⚠️  O arquivo de origem e destino são os mesmos ('{src.name}'). Pulando para evitar sobrescrever.")
        return False

    cmd = [
        FFMPEG, "-nostdin", "-y", "-i", str(src),
        "-map", "0:a:0?", "-map_metadata", "0",
        "-c:a", preset_info['codec'],
        *preset_info['params'],
        "-progress", "pipe:1",
        str(dst)
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, bufsize=1, encoding='utf-8', errors='replace')
    dur = get_duration(str(src)); last_update = time.time()
    bar = tqdm(total=100, desc=f"Convertendo {src.name}", ncols=80, unit="%")
    try:
        for line in proc.stdout:
            if "out_time_ms=" in line:
                try:
                    t = int(line.strip().split("=")[1]) / 1_000_000; pct = min(int(t * 100 / dur), 100)
                    bar.n = pct; bar.refresh(); last_update = time.time()
                except (ValueError, IndexError): continue
            if time.time() - last_update > WATCHDOG_TIMEOUT:
                bar.write(f"⚠️  Sem progresso por {WATCHDOG_TIMEOUT}s. Abortando..."); proc.kill(); break
        bar.n = 100; bar.refresh(); proc.wait()
    finally: bar.close()
    if proc.returncode == 0 and dst.exists() and dst.stat().st_size > 100: print("✅ Conversão de áudio concluída!"); return True
    print(f"❌ Erro na conversão de áudio (código: {proc.returncode})."); dst.unlink(missing_ok=True); return False

def run_audio_convert_logic():
    """Função principal para o fluxo de conversão de áudio."""
    print("\n==========================================================")
    print("=== Modo: Converter Arquivos de ÁUDIO ===")
    print("==========================================================")
    
    # Presets de Qualidade de Áudio
    audio_presets = {
        '1': {'name': 'Lossless (FLAC)', 'codec': 'flac', 'ext': 'flac', 'params': ['-compression_level', '8']},
        '2': {'name': 'Alta Qualidade (MP3, 320kbps CBR)', 'codec': 'libmp3lame', 'ext': 'mp3', 'params': ['-b:a', '320k']},
        '3': {'name': 'Alta Qualidade (AAC/M4A, ~256kbps VBR)', 'codec': 'aac', 'ext': 'm4a', 'params': ['-q:a', '5']},
        '4': {'name': 'Qualidade Média (MP3, 192kbps CBR)', 'codec': 'libmp3lame', 'ext': 'mp3', 'params': ['-b:a', '192k']},
        '5': {'name': 'Qualidade Média (AAC/M4A, ~160kbps VBR)', 'codec': 'aac', 'ext': 'm4a', 'params': ['-q:a', '4']}
    }
    
    print(">> Escolha o formato de ENTRADA (origem):")
    input_ext = input("   Digite a extensão dos arquivos de origem (ex: flac, wav, m4a): ").strip().lower().replace('.', '')
    if not input_ext: print("ERRO: Extensão de entrada não pode ser vazia."); return
        
    print("\n>> Escolha a QUALIDADE e o FORMATO de SAÍDA:")
    for key, value in audio_presets.items(): print(f"   {key}) {value['name']}")
    
    preset_choice = ""
    while preset_choice not in audio_presets:
        preset_choice = input(f"   Digite a opção (1-{len(audio_presets)}): ").strip()
    chosen_preset = audio_presets[preset_choice]
    print(f"   -> Formato de saída será: .{chosen_preset['ext']}")
    
    print("\n>> Após uma conversão bem-sucedida, como lidar com o arquivo original?")
    print("   1) Deletar AUTOMATICAMENTE\n   2) PERGUNTAR antes de deletar [Padrão]")
    delete_mode = "2"; delete_choice = input("   Digite a opção de deleção (1 ou 2): ").strip()
    if delete_choice == "1": delete_mode = "1"

    if not os.path.isfile(FFMPEG) or not os.path.isfile(FFPROBE): print("ERRO: FFmpeg ou FFprobe não encontrado."); return
    input_files = sorted(Path(".").glob(f"*.{input_ext}"))
    if not input_files: print(f"\nNenhum arquivo *.{input_ext} encontrado."); return

    print(f"\nArquivos *.{input_ext} encontrados ({len(input_files)}):")
    for file in input_files: print(f"  {file.name}")
    print("-----------------------------------------------------")
    confirm_batch = input(f">> Confirma a conversão de {len(input_files)} arquivos para '{chosen_preset['name']}'? (s/N): ").strip()
    if confirm_batch.lower() != 's': print("Conversão cancelada."); return

    converted_count, error_count, removed_count, failed_files = 0, 0, 0, []
    for i, input_file in enumerate(input_files):
        if input_file.name == os.path.basename(__file__): continue
        print(f"\n--- [{i+1}/{len(input_files)}] Processando: '{input_file.name}' ---")
        if convert_one_audio(input_file, chosen_preset):
            converted_count += 1
            should_remove = False
            if delete_mode == "1": should_remove = True
            else:
                confirm_rm = input(f"    Remover o original '{input_file.name}'? (s/N): ").strip()
                if confirm_rm.lower() == 's': should_remove = True
            if should_remove:
                try: input_file.unlink(); print(f"     -> Original '{input_file.name}' removido."); removed_count += 1
                except Exception as e: print(f"     -> ERRO ao remover original: {e}"); error_count += 1
            else: print("     -> Original NÃO removido.")
        else: error_count += 1; failed_files.append(input_file.name)
        print("-----------------------------------------------------")
    print("\n======================================================")
    print(f">> Processamento de ÁUDIO Concluído.")
    print(f"- Arquivos convertidos: {converted_count}\n- Originais removidos: {removed_count}\n- Erros: {error_count}")
    if failed_files:
        print(f"- Arquivos que falharam:"); [print(f"  • {f}") for f in failed_files]
    print("======================================================")

# ───────────────────────────── Main ────────────────────────────────
def main():
    """Lógica principal do script multiplataforma"""
    global SCRIPT_DIR
    try:
        if getattr(sys, 'frozen', False): SCRIPT_DIR = os.path.dirname(sys.executable)
        else: SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError: SCRIPT_DIR = os.path.abspath(".")
    os.chdir(SCRIPT_DIR)
    
    banner_color_index = 0
    platform_name = "Android" if IS_ANDROID else ("Windows" if IS_WINDOWS else "Linux")
    
    while True:
        try:
            clear_screen(); print_art(banner_color_index)
            if NUM_BANNER_COLORS > 0: banner_color_index = (banner_color_index + 1) % NUM_BANNER_COLORS
            
            print("==========================================================")
            print(f"=== Menu Principal ({platform_name}) ===")
            print("==========================================================")
            print("Escolha a ação desejada:")
            print("  1) Renomear arquivos de séries")
            print("  2) Converter arquivos de VÍDEO")
            print("  3) Converter arquivos de ÁUDIO")
            print("  *) Sair")
            print()
            
            acao = input("Digite sua opção: ").strip()
            
            if acao == "1": run_rename_logic()
            elif acao == "2": run_video_convert_logic()
            elif acao == "3": run_audio_convert_logic()
            else: print("Saindo."); break
            
            print()
            continue_choice = input("Pressione Enter para voltar ao menu principal ou digite 'sair': ").strip()
            if continue_choice.lower() == "sair": print("Saindo."); break
                
        except KeyboardInterrupt: print("\nSaindo."); break
        except Exception as e: print(f"\nOcorreu um erro inesperado: {e}\nO script será finalizado."); break
    
    print("\nScript finalizado.")

if __name__ == "__main__":
    main()
