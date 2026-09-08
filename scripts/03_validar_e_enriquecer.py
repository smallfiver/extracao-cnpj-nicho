"""Revalida os candidatos contra a base ATUAL da Receita Federal (via a API
publica minhareceita.org) e monta a lista final com contato + responsavel.

Por que revalidar: o arquivo baixado no script 01 pode ter meses de atraso.
Uma empresa "ativa" no arquivo pode ter fechado depois. Este script consulta
o CNPJ completo (calculando os digitos verificadores) na base atual e so
aceita quem estiver mesmo ATIVA hoje.

Padrao "pegar mais N sem repetir": passe --meta com um numero maior que a
ultima vez e --excluir apontando para o CSV/JSON/TXT ja entregue -- o script
para de repetir os CNPJs que ja saiu antes e so soma novos ate a nova meta.
Ex: primeira rodada --meta 10, proxima rodada --meta 20 (mesmo arquivo de
candidatos) --excluir entrega_anterior.txt -> saem so os 10 novos.

Uso:
    python 03_validar_e_enriquecer.py candidatos.json --meta 20 -o final.json
    python 03_validar_e_enriquecer.py candidatos.json --meta 30 -o final.json --excluir final.json
"""
import argparse
import json
import re
import time

from curl_cffi import requests

PAUSA = 0.3  # cortesia com a API publica -- nao acelere isto


def dv_cnpj(base12: str) -> str:
    """Calcula os 2 digitos verificadores do CNPJ a partir dos 12 primeiros
    digitos (8 do cnpj_basico + 4 da ordem, geralmente '0001' para matriz)."""
    def digito(nums, pesos):
        s = sum(int(n) * p for n, p in zip(nums, pesos))
        r = s % 11
        return "0" if r < 2 else str(11 - r)
    d1 = digito(base12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = digito(base12 + d1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return d1 + d2


def cnpj_completo(cnpj_basico: str, ordem: str = "0001") -> str:
    b12 = cnpj_basico.zfill(8) + ordem
    return b12 + dv_cnpj(b12)


def consultar_receita(cnpj: str):
    try:
        r = requests.get(f"https://minhareceita.org/{cnpj}", impersonate="chrome", timeout=25)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def carregar_cnpjs_excluir(caminho):
    """Aceita .txt (um CNPJ por linha), .csv (coluna 'cnpj') ou .json
    (lista de objetos com campo 'cnpj', ou dict de listas de objetos)."""
    if not caminho:
        return set()
    if caminho.endswith(".json"):
        d = json.load(open(caminho, encoding="utf-8"))
        itens = d if isinstance(d, list) else [x for v in d.values() for x in v]
        return {re.sub(r"\D", "", x["cnpj"]) for x in itens if x.get("cnpj")}
    if caminho.endswith(".csv"):
        import csv
        with open(caminho, encoding="utf-8-sig") as fh:
            return {re.sub(r"\D", "", row["cnpj"]) for row in csv.DictReader(fh) if row.get("cnpj")}
    # txt: um CNPJ por linha, com ou sem pontuacao
    return {re.sub(r"\D", "", ln) for ln in open(caminho, encoding="utf-8") if ln.strip()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidatos", help="JSON gerado pelo script 02")
    ap.add_argument("--meta", type=int, default=50, help="quantas empresas validas voce quer no total")
    ap.add_argument("--excluir", default=None, help="arquivo com CNPJs ja entregues antes (txt/csv/json)")
    ap.add_argument("-o", "--saida", default="final.json")
    args = ap.parse_args()

    candidatos = json.load(open(args.candidatos, encoding="utf-8"))
    ja_usados = carregar_cnpjs_excluir(args.excluir)
    if ja_usados:
        print(f"excluindo {len(ja_usados)} CNPJs ja entregues antes")

    aceitos, testados, vistos_contato = [], 0, set()
    for c in candidatos:
        if len(aceitos) >= args.meta:
            break
        cnpj = cnpj_completo(c["cnpj_basico"])
        if cnpj in ja_usados:
            continue
        testados += 1
        d = consultar_receita(cnpj)
        time.sleep(PAUSA)
        if not d or d.get("descricao_situacao_cadastral") != "ATIVA":
            continue

        tel = (d.get("ddd_telefone_1") or "").strip()
        email = (d.get("email") or "").strip()
        if not tel and not email:
            continue

        chave_contato = (tel, email)
        # evita duas empresas com o MESMO contato -- costuma ser o
        # contador que abriu ambas, nao um contato real da empresa
        if chave_contato in vistos_contato:
            continue
        vistos_contato.add(chave_contato)

        qsa = d.get("qsa") or []
        aceitos.append({
            "cnpj": cnpj,
            "razao_social": d.get("razao_social", ""),
            "nome_fantasia": d.get("nome_fantasia") or c.get("fantasia", ""),
            "responsavel": qsa[0].get("nome_socio", "") if qsa else "",
            "qualificacao": qsa[0].get("qualificacao_socio", "") if qsa else "",
            "telefone": tel,
            "email": email,                      # a API atual quase sempre devolve vazio
            "email_arquivo_rf": c.get("email", ""),  # fallback: e-mail do arquivo bruto (script 01/02)
            "cnae": d.get("cnae_fiscal_descricao", ""),
            "municipio": d.get("municipio", ""),
            "uf": d.get("uf", ""),
            "porte": d.get("porte", ""),
            "capital_social": d.get("capital_social", ""),
            "abertura": d.get("data_inicio_atividade", ""),
            "endereco_bairro": c.get("bairro", ""),
            "endereco_cep": c.get("cep", ""),
            "endereco_tipo_logr": c.get("tipo_logr", ""),
            "endereco_logradouro": c.get("logradouro", ""),
            "endereco_numero": c.get("numero", ""),
            "endereco_complemento": c.get("complemento", ""),
        })
        if len(aceitos) % 10 == 0:
            print(f"    {len(aceitos)}/{args.meta} (testados {testados})", flush=True)

    # a API atual normalmente nao devolve e-mail (parece removido por LGPD);
    # recupera do arquivo bruto da RF quando a API veio vazia
    recuperados = 0
    for a in aceitos:
        if not a["email"] and a["email_arquivo_rf"]:
            a["email"] = a["email_arquivo_rf"]
            a["email_origem"] = "arquivo RF (pode estar desatualizado)"
            recuperados += 1

    print(f"\nFINAL: {len(aceitos)} empresas validas (de {testados} testadas)")
    print(f"e-mails recuperados do arquivo bruto: {recuperados}")
    json.dump(aceitos, open(args.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK -> {args.saida}")


if __name__ == "__main__":
    main()
