# Como publicar isto para o seu mentorado

O repositório já está publicado e a `MENSAGEM_PARA_MENTORADO.md` já tem a
URL preenchida:

**https://github.com/smallfiver/extracao-cnpj-nicho**

Ele é **privado** — falta só dar acesso ao seu mentorado antes de mandar a
mensagem.

## Dar acesso (repositório privado)

```bash
gh repo add-collaborator smallfiver/extracao-cnpj-nicho <usuario-github-do-mentorado>
```

Ou pela interface: no repositório, `Settings` → `Collaborators` →
`Add people`, e digite o usuário ou e-mail do GitHub dele. O GitHub manda um
convite que ele precisa aceitar antes de conseguir clonar.

Se preferir deixar público em vez de dar acesso individual (sem dados
sensíveis no código, só os scripts):

```bash
gh repo edit smallfiver/extracao-cnpj-nicho --visibility public --accept-visibility-change-consequences
```

## Sem GitHub — alternativa por arquivo

Se em algum momento preferir não depender do GitHub, compacte a pasta
inteira `extracao-cnpj-nicho` num .zip e mande direto. Nesse caso, troque o
passo 4 da mensagem (`git clone ...`) por:

```
4. Extraia o arquivo .zip que vou te mandar dentro da pasta
   .claude/skills/, de forma que fique
   .claude/skills/extracao-cnpj-nicho/SKILL.md
```

## Atualizando depois

Se você melhorar a skill no futuro (novos CNAEs, correção de bug), edite os
arquivos em `C:\Users\alexw\.claude\skills\extracao-cnpj-nicho`, depois:

```bash
cd "C:\Users\alexw\.claude\skills\extracao-cnpj-nicho"
git add -A
git commit -m "descreva a mudanca"
git push
```

Seu mentorado só precisa rodar `git pull` dentro da pasta da skill dele —
não precisa reinstalar nada.
