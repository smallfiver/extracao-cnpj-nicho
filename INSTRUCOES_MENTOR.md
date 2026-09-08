# Como publicar isto para o seu mentorado

Este repositório já está pronto e commitado localmente (veja o resultado
que o Claude te mostrou). Falta só colocar num lugar que o Claude do seu
mentorado consiga clonar. Duas opções, escolha uma:

## Opção A — GitHub (recomendado, mais fácil de manter/atualizar depois)

Se você tem o GitHub CLI (`gh`) autenticado:

```bash
cd "C:\Users\alexw\.claude\skills\extracao-cnpj-nicho"
gh repo create extracao-cnpj-nicho --private --source=. --remote=origin --push
```

Isso cria o repositório na sua conta e já sobe o código. Copie a URL que
aparecer (algo como `https://github.com/SEU_USUARIO/extracao-cnpj-nicho`) e
cole no lugar de `<URL-DO-REPO>` em `MENSAGEM_PARA_MENTORADO.md`.

Se não tiver o `gh` instalado, crie o repositório manualmente em
github.com/new (pode ser privado), depois:

```bash
git remote add origin https://github.com/SEU_USUARIO/extracao-cnpj-nicho.git
git push -u origin main
```

Se o repositório for **privado**, seu mentorado vai precisar de acesso
(adicione o GitHub dele como colaborador) ou de um token de acesso para
clonar.

## Opção B — Sem GitHub, direto por arquivo

Se preferir não usar GitHub, é só compactar a pasta inteira
`extracao-cnpj-nicho` num .zip e mandar pro seu mentorado. Nesse caso, no
passo 4 da mensagem, troque a instrução de `git clone` por:

```
4. Extraia o arquivo .zip que vou te mandar dentro da pasta
   .claude/skills/, de forma que fique
   .claude/skills/extracao-cnpj-nicho/SKILL.md
```

## Atualizando depois

Se você melhorar a skill no futuro (novos CNAEs, correção de bug), só
precisa dar `git push` de novo (Opção A) e seu mentorado roda `git pull`
dentro da pasta da skill dele — não precisa reinstalar nada.
