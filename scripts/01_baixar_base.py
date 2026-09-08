"""Baixa a base de dados abertos do CNPJ (Receita Federal).

O servidor oficial (dadosabertos.rfb.gov.br) costuma cair ou recusar conexao.
Este script tenta o oficial primeiro com timeout curto e cai para um mirror
publico no GitHub se ele falhar -- foi exatamente o que aconteceu na pratica.

Uso:
    python 01_baixar_base.py [pasta_destino]

Baixa ~1.9 GB (Empresas, Estabelecimentos, Socios) + tabelas de apoio
(Municipios). So roda o que ainda nao existe no destino.
"""
import os
import sys

from curl_cffi import requests

DESTINO = sys.argv[1] if len(sys.argv) > 1 else "./dados_rf"
ARQUIVOS = ["Empresas0.zip", "Estabelecimentos0.zip", "Socios0.zip", "Municipios.zip"]

OFICIAL = "https://dadosabertos.rfb.gov.br/CNPJ/dados_abertos_cnpj/{mes}/{arquivo}"
MESES_TENTAR = ["2026-08", "2026-07", "2026-06", "2026-01"]  # tenta os mais recentes primeiro


def tentar_oficial(arquivo, destino_arquivo):
    for mes in MESES_TENTAR:
        url = OFICIAL.format(mes=mes, arquivo=arquivo)
        try:
            r = requests.head(url, impersonate="chrome", timeout=8)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None


def achar_release_mirror():
    """O mirror no GitHub sobe uma release nova a cada atualizacao da RF.
    Pega a mais recente automaticamente em vez de fixar uma data."""
    try:
        r = requests.get(
            "https://api.github.com/repos/jonathands/dados-abertos-receita-cnpj/releases/latest",
            impersonate="chrome", timeout=15)
        if r.status_code == 200:
            return r.json()["tag_name"]
    except Exception:
        pass
    return "2024.09"  # fallback conhecido, funcionava em 2026-09


def baixar(url, destino_arquivo):
    print(f"  baixando de: {url}", flush=True)
    r = requests.get(url, stream=True, impersonate="chrome", timeout=3600)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    feito = marco = 0
    with open(destino_arquivo, "wb") as fh:
        for chunk in r.iter_content(chunk_size=1 << 20):
            fh.write(chunk)
            feito += len(chunk)
            if feito - marco >= (200 << 20):
                marco = feito
                print(f"    {feito/1048576:.0f}/{total/1048576:.0f} MB", flush=True)
    print(f"  ok -> {os.path.getsize(destino_arquivo)/1048576:.1f} MB", flush=True)


def main():
    os.makedirs(DESTINO, exist_ok=True)
    tag_mirror = None

    for nome in ARQUIVOS:
        alvo = os.path.join(DESTINO, nome)
        if os.path.exists(alvo) and os.path.getsize(alvo) > 1024:
            print(f"[ja existe] {nome} ({os.path.getsize(alvo)/1048576:.1f} MB)")
            continue

        print(f"[buscando] {nome} ...")
        url = tentar_oficial(nome, alvo)
        if not url:
            if tag_mirror is None:
                tag_mirror = achar_release_mirror()
                print(f"  servidor oficial indisponivel -- usando mirror ({tag_mirror})")
            url = (f"https://github.com/jonathands/dados-abertos-receita-cnpj/"
                   f"releases/download/{tag_mirror}/{nome}")
        try:
            baixar(url, alvo)
        except Exception as e:
            print(f"  [FALHOU] {nome}: {type(e).__name__} {e}")
            print(f"  tente baixar manualmente e colocar em {alvo}")

    print("\nDOWNLOAD CONCLUIDO (ou ja estava tudo la).")
    print(f"Pasta: {os.path.abspath(DESTINO)}")


if __name__ == "__main__":
    main()
