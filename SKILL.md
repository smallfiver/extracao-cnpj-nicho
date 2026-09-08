---
name: extracao-cnpj-nicho
description: Extrai listas de empresas brasileiras (CNPJ) de um nicho/segmento especifico -- por CNAE, estado, cidade ou ate bairro -- a partir da base publica e gratuita de dados abertos da Receita Federal, validando cada uma como ATIVA na base atual e trazendo telefone, e-mail e nome do responsavel (socio/administrador). Use esta skill sempre que o usuario pedir uma lista de empresas/CNPJs/leads B2B para prospeccao por segmento (ex: "academias no Rio", "construtoras em SP", "10 CNPJs de marketing", "empresas de logistica"), pedir para expandir uma lista existente com "mais N novos" sem repetir os que ja foram entregues, ou pedir para exportar essa lista em formato de WhatsApp, CSV, ou para importar localizacoes no Meta Ads Manager. Nao use para dados de pessoa fisica fora do contexto de responsavel legal de uma empresa, nem para servicos pagos tipo cnpj.biz/Serasa (isso e' SaaS de terceiro, nao dado publico).
---

# Extracao de CNPJ por nicho

Monta listas de empresas ativas de um segmento especifico usando **dados
publicos e gratuitos** da Receita Federal (nao um SaaS de terceiro tipo
cnpj.biz, que cobra por isso e coloca a busca por segmento atras de login).

## Antes de comecar: o ambiente

Isto precisa de Python 3.12/3.13 com `curl_cffi` instalado (vem junto se o
usuario instalou o pacote `scrapling[fetchers,shell]`, ou instale so
`curl_cffi` isoladamente -- e' a unica dependencia externa real). Rode tudo
dentro de um venv dedicado, nunca no Python global do sistema.

Se a pasta de trabalho estiver dentro do Google Drive/OneDrive/Dropbox, os
downloads e a criacao do venv ficam bem mais lentos (a sincronizacao tenta
acompanhar cada arquivo). Funciona, so avise o usuario que pode demorar.

## O fluxo (4 passos, cada um e' um script em `scripts/`)

### 1. Baixar a base da Receita -- `01_baixar_base.py`

```bash
python scripts/01_baixar_base.py ./dados_rf
```

Baixa ~1.9 GB: `Empresas0.zip`, `Estabelecimentos0.zip`, `Socios0.zip`,
`Municipios.zip`. **O servidor oficial da Receita (`dadosabertos.rfb.gov.br`)
costuma recusar conexao** -- ja aconteceu em producao. O script tenta o
oficial com timeout curto e cai automaticamente para um mirror publico no
GitHub se precisar. So baixa o que ainda nao existir na pasta.

So precisa rodar de novo quando quiser dados mais recentes (a Receita
atualiza mensalmente); para varias extracoes na mesma sessao de trabalho,
reaproveite a mesma pasta `dados_rf`.

### 2. Achar candidatos por CNAE -- `02_buscar_candidatos.py`

Antes de rodar, confira `references/cnaes_comuns.md` -- ja tem CNAEs prontos
para imobiliaria, construtora, logistica, marketing e academia. Para um
nicho novo, pesquise o CNAE (veja a secao "como achar CNAE" nesse arquivo).

```bash
# nicho generico, Brasil inteiro, ate 400 candidatos
python scripts/02_buscar_candidatos.py --cnae 7311400,7319004 --cota 400 -o candidatos.json

# filtrando por estado
python scripts/02_buscar_candidatos.py --cnae 9313100 --uf RJ,SP --cota 400 -o candidatos.json

# filtrando por bairro dentro de uma cidade (cobertura de 100%, sem cota)
python scripts/02_buscar_candidatos.py --listar-municipios --bairro "RIO DE JANEIRO" -d ./dados_rf
# (acha o codigo do municipio, ex: 6001)
python scripts/02_buscar_candidatos.py --cnae 9313100 --municipio 6001 --bairro "RECREIO" -o recreio.json
```

Isto varre ~20 milhoes de linhas -- demora alguns minutos, rode em background
se a ferramenta disponivel suportar isso.

**Cuidado com CNAE generico demais.** Um CNAE "genérico" (tipo "Promoção de
vendas" para marketing) vira um balaio que atrai empresas de outros ramos e
contamina o nicho. Depois de rodar, confira a distribuicao de CNAE nos
resultados (`cnae_desc` de cada item) antes de escalar -- se um CNAE tomar
conta e trouxer lixo, tire ele da lista de `--cnae` e rode de novo.

### 3. Validar como ativa hoje + enriquecer -- `03_validar_e_enriquecer.py`

O arquivo baixado no passo 1 pode ter meses de atraso -- uma empresa "ativa"
nele pode ter fechado depois. Este passo consulta a API publica
`minhareceita.org` (calcula os digitos verificadores do CNPJ sozinho) e so
aceita quem estiver **ATIVA agora**.

```bash
python scripts/03_validar_e_enriquecer.py candidatos.json --meta 20 -o final.json
```

Traz `razao_social`, `nome_fantasia`, `responsavel` (nome do socio/QSA),
telefone e e-mail. Filtra automaticamente contato falso (telefone tipo
5555-5555, e-mail@e-mail.com) e evita duas empresas com o **mesmo** contato
(comum quando e' o contador que abriu ambas -- nao e' contato real da
empresa).

**Pedido de "mais N novos" sem repetir os que ja sairam:** e' o padrao mais
comum depois da primeira entrega. Basta rodar de novo com `--meta` maior e
`--excluir` apontando pro arquivo ja entregue -- aceita `.txt` (um CNPJ por
linha), `.csv` (coluna `cnpj`) ou o proprio `.json` de saida anterior:

```bash
# ja tinha 20, usuario pediu mais 10 -> pede 30 no total, exclui os 20 de antes
python scripts/03_validar_e_enriquecer.py candidatos.json --meta 30 -o final.json --excluir final.json
```

Se o pool de `candidatos.json` esgotar (poucos "testados" novos por rodada,
ou `FINAL` ficar bem abaixo de `--meta`), volte ao passo 2 com uma cota
maior ou mais CNAEs para reabastecer o pool.

**Nota de privacidade:** o nome do responsavel e' dado pessoal (LGPD). Para
uso comercial B2B isso se sustenta em legitimo interesse, mas avise o
usuario para citar a origem (dado publico da Receita) e oferecer opt-out no
primeiro contato -- nao deixe passar batido.

### 4. Exportar no formato que o usuario vai usar -- `04_exportar.py`

```bash
python scripts/04_exportar.py final.json --formatos csv,whatsapp,cnpjs
python scripts/04_exportar.py final.json --formatos meta-enderecos --titulo "ACADEMIAS RJ"
```

- `csv` -- UTF-8 com BOM (abre acentuado certo no Excel)
- `whatsapp` -- texto com `*negrito*` pronto pra colar numa conversa
- `cnpjs` -- so os CNPJs (formatado com pontuacao E so digitos, dois arquivos)
- `meta-enderecos` -- formato `Rua, Numero, Cidade, UF, Brasil` para colar na
  caixa "Adicionar localizacoes em massa" do Meta Ads Manager (tipo de
  localizacao = Enderecos). Trata numero ausente, complemento (SALA/LOJA/APT)
  e enderecos por Quadra/Lote (comum em cidades planejadas como Goiania e
  Brasilia) automaticamente.

## Coisas que já deram errado antes (para não repetir)

- **Console do Windows quebra acento em texto UTF-8** (aparece `?` no
  terminal). Isso e' so exibicao -- confira com `ord()`/`repr()` antes de
  achar que o dado esta corrompido; o arquivo salvo em UTF-8 costuma estar
  correto.
- **Raio minimo do Meta Ads e' 1,6 km.** Mesmo com endereco exato (nao so
  CEP), o pin vira um circulo desse tamanho -- em capital isso cobre um
  bairro inteiro, nao "quem frequenta aquele endereco". Avise o usuario: se
  o objetivo e' atingir o publico de um nicho (ex: fitness) em cidade
  grande, segmentar por **interesse** costuma funcionar melhor que raio.
- **CNPJ.biz e sites parecidos sao SaaS pago**, nao dado aberto -- a busca
  por segmento deles fica atras de login/plano. Nao tente raspar aquilo;
  use esta skill para pegar o mesmo tipo de dado direto da fonte publica.
- **Endereco com "APT"** no complemento geralmente e' cadastro fiscal de
  autonomo/personal, nao um estabelecimento aberto ao publico -- vale
  avisar se o uso for campanha fisica/parceria local.

## Estrutura da skill

```
extracao-cnpj-nicho/
├── SKILL.md                          (este arquivo)
├── references/
│   └── cnaes_comuns.md               (CNAEs prontos + como achar novos)
└── scripts/
    ├── 01_baixar_base.py             (baixa a base da Receita)
    ├── 02_buscar_candidatos.py       (filtra por CNAE/UF/municipio/bairro)
    ├── 03_validar_e_enriquecer.py    (valida ATIVA hoje + contato + dedup)
    └── 04_exportar.py                (csv / whatsapp / cnpjs / meta-enderecos)
```
