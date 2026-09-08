"""Varre o arquivo Estabelecimentos da Receita Federal filtrando por CNAE
(e opcionalmente UF e/ou bairro) e salva os candidatos brutos em JSON.

So le o zip em streaming (nao extrai para disco) -- o arquivo tem ~19-20
milhoes de linhas, entao a varredura demora alguns minutos.

Uso basico (todo o Brasil, um ou mais CNAEs):
    python 02_buscar_candidatos.py --cnae 7311400,7319004 --cota 200 -o candidatos.json

Filtrando por estado(s):
    python 02_buscar_candidatos.py --cnae 9313100 --uf SP,RJ,MG --cota 400 -o candidatos.json

Filtrando por bairro dentro de um municipio (cobertura de 100%, ignora cota):
    python 02_buscar_candidatos.py --cnae 9313100 --municipio 6001 --bairro "RECREIO" -o recreio.json

O codigo de municipio (--municipio) e o codigo INTERNO da Receita, nao o
IBGE -- para descobrir o codigo de uma cidade, rode com --listar-municipios
depois de ter o Municipios.zip baixado (script 01).
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import zipfile

# indices das colunas no arquivo Estabelecimentos (layout oficial, sem cabecalho)
C_BASICO, C_MATRIZ, C_FANTASIA, C_SIT = 0, 3, 4, 5
C_INICIO, C_CNAE = 10, 11
C_TIPO_LOGR, C_LOGR, C_NUM, C_COMPL, C_BAIRRO = 13, 14, 15, 16, 17
C_CEP, C_UF, C_MUN = 18, 19, 20
C_DDD, C_TEL, C_DDD2, C_TEL2, C_DDD_FAX, C_FAX, C_EMAIL = 21, 22, 23, 24, 25, 26, 27
ATIVA = "02"

EMAILS_LIXO = {"email@email.com", "teste@teste.com", "a@a.com", "x@x.com",
               "nao@tem.com", "naotem@naotem.com", "sem@email.com"}


def contato_valido(tel, email):
    """Descarta preenchimento falso de cadastro (5555-5555, email@email.com...)."""
    if tel:
        d = "".join(c for c in tel if c.isdigit())
        if len(set(d)) <= 2:            # digito repetido (1111111111, 5555555555)
            tel = ""
    if email:
        if (email in EMAILS_LIXO or email.count("@") != 1
                or "." not in email.split("@")[-1]):
            email = ""
    return tel, email


def linhas_do_zip(caminho):
    with zipfile.ZipFile(caminho) as z:
        interno = z.namelist()[0]
        with z.open(interno) as bruto:
            txt = io.TextIOWrapper(bruto, encoding="latin-1", newline="")
            yield from csv.reader(txt, delimiter=";", quotechar='"')


def carregar_municipios(pasta_dados):
    caminho = os.path.join(pasta_dados, "Municipios.zip")
    if not os.path.exists(caminho):
        return {}
    mapa = {}
    for row in linhas_do_zip(caminho):
        if len(row) >= 2:
            mapa[row[0].strip()] = row[1].strip()
    return mapa


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cnae", required=False, help="CNAEs separados por virgula (7 digitos cada)")
    ap.add_argument("--uf", default=None, help="UFs separadas por virgula (opcional, ex: SP,RJ)")
    ap.add_argument("--municipio", default=None, help="codigo de municipio da Receita (opcional)")
    ap.add_argument("--bairro", default=None, help="substring do bairro, sem acento maiusculo (opcional)")
    ap.add_argument("--so-ativas", action="store_true", default=True, help="so situacao ATIVA (padrao: sim)")
    ap.add_argument("--so-matriz", action="store_true", default=True, help="so matriz, nao filial (padrao: sim)")
    ap.add_argument("--exigir-contato", action="store_true", default=True,
                     help="exige telefone ou email valido (padrao: sim)")
    ap.add_argument("--cota", type=int, default=400, help="maximo de candidatos (ignorado se --bairro)")
    ap.add_argument("-d", "--dados", default="./dados_rf", help="pasta com os zips da Receita (script 01)")
    ap.add_argument("-o", "--saida", default="candidatos.json")
    ap.add_argument("--listar-municipios", action="store_true",
                     help="so lista municipios cujo nome contem --bairro/--uf e sai (nao varre Estabelecimentos)")
    args = ap.parse_args()

    municipios = carregar_municipios(args.dados)

    if args.listar_municipios:
        alvo = (args.bairro or "").upper()
        for cod, nome in municipios.items():
            if alvo in nome:
                print(f"{cod}  {nome}")
        return

    if not args.cnae:
        ap.error("--cnae e obrigatorio (a menos que use --listar-municipios)")

    cnaes = {c.strip() for c in args.cnae.split(",")}
    ufs = {u.strip().upper() for u in args.uf.split(",")} if args.uf else None
    bairro_alvo = args.bairro.upper() if args.bairro else None
    sem_cota = bairro_alvo is not None or args.municipio is not None

    caminho_estab = os.path.join(args.dados, "Estabelecimentos0.zip")
    if not os.path.exists(caminho_estab):
        sys.exit(f"Nao achei {caminho_estab}. Rode antes: python 01_baixar_base.py {args.dados}")

    print(f"Filtrando: CNAE={sorted(cnaes)} UF={ufs or 'todas'} "
          f"municipio={args.municipio or 'todos'} bairro={bairro_alvo or '-'}")

    achados = []
    lidas = 0
    for c in linhas_do_zip(caminho_estab):
        lidas += 1
        if lidas % 5_000_000 == 0:
            print(f"  {lidas:,} linhas | {len(achados)} candidatos ate agora", flush=True)
        if len(c) < 28:
            continue
        if c[C_CNAE] not in cnaes:
            continue
        if args.so_ativas and c[C_SIT] != ATIVA:
            continue
        if args.so_matriz and c[C_MATRIZ] != "1":
            continue
        if ufs and c[C_UF] not in ufs:
            continue
        if args.municipio and c[C_MUN] != args.municipio:
            continue
        if bairro_alvo and bairro_alvo not in c[C_BAIRRO].upper():
            continue

        tel = (c[C_DDD].strip() + c[C_TEL].strip()).strip()
        email = c[C_EMAIL].strip().lower()
        if args.exigir_contato:
            tel, email = contato_valido(tel, email)
            if not tel and not email:
                continue

        achados.append({
            "cnpj_basico": c[C_BASICO],
            "fantasia": c[C_FANTASIA].strip(),
            "cnae": c[C_CNAE],
            "situacao": c[C_SIT],
            "abertura": c[C_INICIO].strip(),
            "tipo_logr": c[C_TIPO_LOGR].strip(),
            "logradouro": c[C_LOGR].strip(),
            "numero": c[C_NUM].strip(),
            "complemento": c[C_COMPL].strip(),
            "bairro": c[C_BAIRRO].strip(),
            "cep": c[C_CEP].strip(),
            "uf": c[C_UF].strip(),
            "municipio_cod": c[C_MUN].strip(),
            "municipio_nome": municipios.get(c[C_MUN].strip(), ""),
            "telefone": tel,
            "email": email,
        })
        if not sem_cota and len(achados) >= args.cota:
            print(f"  cota atingida em {lidas:,} linhas", flush=True)
            break

    print(f"\ntotal de linhas lidas: {lidas:,}")
    print(f"candidatos encontrados: {len(achados)}")
    json.dump(achados, open(args.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK -> {args.saida}")


if __name__ == "__main__":
    main()
