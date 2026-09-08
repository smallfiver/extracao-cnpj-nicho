# Extração de CNPJ por nicho

Skill do Claude Code para montar listas de empresas brasileiras ativas por
segmento (CNAE), estado, cidade ou bairro — usando a base **pública e
gratuita** de dados abertos da Receita Federal. Sem SaaS pago, sem paywall.

## Instalação

**1. Coloque esta pasta dentro de `.claude/skills/` do seu projeto ou perfil.**

Se você recebeu isto como um repositório git, clone direto no lugar certo:

```bash
git clone <URL-DO-REPO> "C:\Users\SEU_USUARIO\.claude\skills\extracao-cnpj-nicho"
```

(No Mac/Linux seria `~/.claude/skills/extracao-cnpj-nicho`.)

**2. Garanta um ambiente Python com `curl_cffi`.**

A forma mais simples é ter o pacote `scrapling` instalado num venv dedicado
— ele já traz `curl_cffi` como dependência e serve para outros scrapes no
futuro:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install "scrapling[fetchers,shell]"
```

Se preferir só o mínimo necessário para esta skill, basta:

```bash
.venv\Scripts\python.exe -m pip install curl_cffi
```

**3. Peça pro Claude usar a skill.** Basta pedir uma lista de empresas por
segmento (ex: "me tira 15 CNPJs de construtora em SP") — a skill dispara
sozinha. Se quiser rodar os scripts manualmente, veja o `SKILL.md`.

## O que você recebe

Para cada empresa: razão social, nome fantasia, nome do responsável
(sócio/administrador), telefone, e-mail, CNAE, cidade/UF, porte e CNPJ —
tudo validado como **ativo hoje** na base atual da Receita, não só no
arquivo baixado (que pode ter meses de atraso).

Exporta em CSV, texto formatado pra WhatsApp, lista de CNPJs, ou no formato
que o Meta Ads Manager aceita para localização em massa.

## Aviso de uso

Os dados são públicos (Lei de Acesso à Informação / Receita Federal), mas o
nome do responsável é dado pessoal sob a LGPD. Para prospecção B2B isso se
sustenta em legítimo interesse — mas sempre cite a origem pública do dado e
ofereça opção de descadastro no primeiro contato.
