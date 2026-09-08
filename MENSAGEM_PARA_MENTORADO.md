# Mensagem para o mentorado colar no Claude Code dele

Copie tudo dentro da caixa abaixo (do "Estou começando..." até o final) e
cole numa conversa nova do Claude Code do seu mentorado. Antes de enviar,
troque `https://github.com/smallfiver/extracao-cnpj-nicho.git` pela URL real do repositório (veja
`INSTRUCOES_MENTOR.md` na raiz para saber como publicar).

---

```
Estou começando do zero nesta máquina. Preciso que você configure meu
ambiente de scraping e instale uma skill de extração de CNPJ por nicho.

1. Verifique se Python 3.12 ou 3.13 está instalado. Se não estiver, instale
   usando um método que NÃO exija permissão de administrador (ex: winget
   com --scope user, ou o instalador oficial do python.org marcando "Install
   for me only").

2. Crie um ambiente virtual (venv) dedicado numa pasta minha de trabalho —
   não instale nada no Python global da máquina.

3. Dentro desse venv, instale o pacote:
   scrapling[fetchers,shell]
   E rode o comando de instalação dos navegadores dele.

4. Clone este repositório dentro da minha pasta de skills do Claude Code
   (crie a pasta .claude/skills se ela não existir):
   git clone https://github.com/smallfiver/extracao-cnpj-nicho.git .claude/skills/extracao-cnpj-nicho

5. Depois de tudo instalado, teste a skill: baixe a base de dados abertos
   do CNPJ da Receita Federal (o script 01_baixar_base.py dentro da skill
   faz isso) e extraia 10 CNPJs de "academias" (CNAE 9313100) só para
   confirmar que está tudo funcionando — me mostre o resultado.

Me diga o que você vai fazer antes de cada passo.
```

---

## Depois da instalação

A partir daí, seu mentorado só precisa pedir em linguagem natural, por
exemplo:

- "me tira 15 CNPJs de construtora no Rio de Janeiro"
- "quero uma lista de academias em Belo Horizonte, só o endereço"
- "extrai mais 10 novos desse nicho, sem repetir os que já peguei"
- "exporta essa lista pro WhatsApp" / "formata pro Meta Ads"

A skill (`extracao-cnpj-nicho`) dispara sozinha quando o Claude dele
reconhece esse tipo de pedido — não precisa invocar nada manualmente.
