"""Exporta a lista final (script 03) nos formatos mais usados:

  csv          -- planilha completa, UTF-8 com BOM (abre acentuado no Excel)
  whatsapp     -- texto com *negrito* pronto pra colar numa conversa
  cnpjs        -- so os CNPJs, formatados e em digitos puros
  meta-precos  -- (nao existe, ignorar -- placeholder)
  meta-enderecos -- endereco no formato da caixa "Adicionar localizacoes em
                    massa" do Meta Ads Manager (Rua, Numero, Cidade, UF, Brasil)

Uso:
    python 04_exportar.py final.json --formatos csv,whatsapp,cnpjs
    python 04_exportar.py final.json --formatos meta-enderecos --titulo "ACADEMIAS SP"
"""
import argparse
import csv
import json
import re


TIPOS_LOGRADOURO = {"rua", "avenida", "alameda", "travessa", "rodovia", "estrada",
                     "praca", "largo", "via", "viela", "ladeira", "estrada"}
RUIDO = re.compile(
    r"\b(SALA|LOJA|APT|APTO|BLOCO|BLC|ANDAR|COND|CONJ|TERREO|SOBRELOJA|"
    r"EDIF|TORRE|CASA(?!\s)|CX\s?PST|SLJ|PARTE|SAL)\b", re.I)
QUADRA = re.compile(r"\b(?:QUADRA|QD)\.?\s*0*([A-Z0-9]+)\b", re.I)
LOTE = re.compile(r"\b(?:LOTE|LT)\.?\s*0*([A-Z0-9]+)\b", re.I)


def titulo(s):
    return " ".join(w.capitalize() for w in s.split())


def remove_tipo_duplicado(rua_titulo):
    """Corrige bug comum no cadastro de origem: 'Rua X De Andrade Rua' -> 'Rua X De Andrade'."""
    palavras = rua_titulo.split()
    if len(palavras) > 2 and palavras[-1].lower() in TIPOS_LOGRADOURO:
        palavras = palavras[:-1]
    return " ".join(palavras)


def limpa_numero(num):
    num = num.strip().lstrip("0") or "0"
    return "" if num in ("0", "SN", "S/N") else num


def endereco_meta(item):
    """Rua+numero, Cidade, UF, Brasil -- ou Quadra/Lote quando nao ha numero
    de rua tradicional (comum em cidades planejadas como Goiania/Brasilia)."""
    tipo = (item.get("endereco_tipo_logr", "") or "").strip()
    logr = (item.get("endereco_logradouro", "") or "").strip()
    # nao duplica o tipo se o logradouro ja comecar com a mesma palavra
    # (ex: tipo_logr='QUADRA' + logradouro='QUADRA 2 CONJUNTO A...')
    if tipo and logr.upper().startswith(tipo.upper()):
        tipo = ""
    rua = remove_tipo_duplicado(titulo(f"{tipo} {logr}".strip()))
    compl = item.get("endereco_complemento", "") or ""
    numero = item.get("endereco_numero", "") or ""

    m = RUIDO.search(compl)
    livre = (compl[:m.start()] if m else compl).strip(" -")
    loc = ""
    if numero and limpa_numero(numero):
        loc = limpa_numero(numero)
    if not loc:
        bruto = f"{item.get('endereco_logradouro','')} {compl} {numero}"
        qd, lt = QUADRA.search(bruto), LOTE.search(bruto)
        partes = []
        if qd:
            partes.append(f"Quadra {qd.group(1).upper()}")
        if lt:
            partes.append(f"Lote {lt.group(1).upper()}")
        loc = ", ".join(partes)

    cidade = titulo(item.get("municipio", "") or item.get("endereco_municipio", ""))
    uf = item.get("uf", "")
    base = f"{rua}, {loc}" if loc else rua
    return f"{base}, {cidade}, {uf}, Brasil"


def cnpj_fmt(c):
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def fone_fmt(t):
    d = "".join(ch for ch in (t or "") if ch.isdigit())
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return t or "-"


def exportar_csv(itens, base):
    cols = ["razao_social", "nome_fantasia", "responsavel", "qualificacao",
            "telefone", "email", "cnae", "municipio", "uf", "porte",
            "capital_social", "abertura", "cnpj"]
    with open(f"{base}.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(itens)
    print(f"  {base}.csv ({len(itens)} linhas)")


def exportar_whatsapp(itens, base, titulo_lista):
    linhas = [f"*{titulo_lista}*", ""]
    for i, e in enumerate(itens, 1):
        linhas.append(f"*{i}. {e['razao_social']}*")
        if e.get("nome_fantasia") and e["nome_fantasia"] != e["razao_social"]:
            linhas.append(f"   {e['nome_fantasia']}")
        linhas.append(f"   Resp: {e.get('responsavel','-')}")
        linhas.append(f"   Tel: {fone_fmt(e['telefone'])}")
        linhas.append(f"   Email: {e.get('email') or '-'}")
        linhas.append(f"   {e.get('municipio','')}/{e.get('uf','')} - {e.get('porte','')}")
        linhas.append(f"   CNPJ: {cnpj_fmt(e['cnpj'])}")
        linhas.append("")
    caminho = f"{base}_whatsapp.txt"
    open(caminho, "w", encoding="utf-8").write("\n".join(linhas))
    print(f"  {caminho}")


def exportar_cnpjs(itens, base):
    puros = [e["cnpj"] for e in itens]
    fmts = [cnpj_fmt(c) for c in puros]
    open(f"{base}_cnpjs.txt", "w", encoding="utf-8").write("\n".join(fmts))
    open(f"{base}_cnpjs_puro.txt", "w", encoding="utf-8").write("\n".join(puros))
    print(f"  {base}_cnpjs.txt / {base}_cnpjs_puro.txt ({len(puros)} CNPJs)")


def exportar_meta_enderecos(itens, base):
    linhas = [endereco_meta(e) for e in itens]
    caminho = f"{base}_meta_enderecos.txt"
    open(caminho, "w", encoding="utf-8").write("\n".join(linhas))
    print(f"  {caminho} ({len(linhas)} enderecos)")
    print("  cole na caixa 'Adicionar localizacoes em massa' do Meta Ads")
    print("  Tipo de localizacao: Enderecos -- um por linha ja funciona.")
    sem_locador = [l for l in linhas if l.count(",") < 3]
    if sem_locador:
        print(f"  aviso: {len(sem_locador)} endereco(s) sem numero/quadra identificavel -- confira manualmente")
    tipos_complexos = {"SETOR", "ENTRE QUADRA", "QUADRA", "SQN", "SQS", "SHSN", "SHIS", "SHIN"}
    complexos = [e for e in itens if (e.get("endereco_tipo_logr", "") or "").upper() in tipos_complexos]
    if complexos:
        print(f"  aviso: {len(complexos)} endereco(s) usam sistema de endereçamento de "
              "cidade planejada (Brasilia/Goiania) -- a formatacao automatica pode ficar "
              "confusa, confira manualmente antes de subir no Meta")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="JSON gerado pelo script 03")
    ap.add_argument("--formatos", default="csv,whatsapp,cnpjs",
                     help="csv,whatsapp,cnpjs,meta-enderecos (separados por virgula)")
    ap.add_argument("--titulo", default="LISTA DE EMPRESAS", help="titulo do texto de WhatsApp")
    ap.add_argument("-o", "--base", default=None, help="prefixo dos arquivos de saida (padrao: nome do JSON)")
    args = ap.parse_args()

    itens = json.load(open(args.entrada, encoding="utf-8"))
    if isinstance(itens, dict):  # aceita tanto lista quanto {nicho: [...]}
        itens = [x for v in itens.values() for x in v]

    base = args.base or args.entrada.rsplit(".", 1)[0]
    formatos = {f.strip() for f in args.formatos.split(",")}

    if "csv" in formatos:
        exportar_csv(itens, base)
    if "whatsapp" in formatos:
        exportar_whatsapp(itens, base, args.titulo)
    if "cnpjs" in formatos:
        exportar_cnpjs(itens, base)
    if "meta-enderecos" in formatos:
        exportar_meta_enderecos(itens, base)


if __name__ == "__main__":
    main()
