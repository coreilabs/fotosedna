# Instruções do projeto

## Versionamento obrigatório de scripts e estilos

- Ao concluir qualquer modificação no projeto, execute `python scripts/version_assets.py --force` antes da entrega ou publicação.
- Force novas versões mesmo quando o conteúdo dos arquivos JavaScript e CSS não tiver mudado. Executar sem `--force` não atende a esta regra.
- Confirme que as URLs dos scripts e estilos em `index.html`, e a importação do PhotoSwipe em `assets/app.js`, receberam os novos parâmetros `?v=`. Inclua essas alterações na entrega.
- Preserve as preferências globais de validação no Chrome e uso da instalação compartilhada do Playwright.
