# Instruções do projeto

## Versionamento obrigatório de scripts e estilos

- Ao concluir qualquer modificação no projeto, execute `python scripts/version_assets.py --force` antes da entrega ou publicação.
- Force novas versões mesmo quando o conteúdo dos arquivos JavaScript e CSS não tiver mudado. Executar sem `--force` não atende a esta regra.
- Confirme que as URLs dos scripts e estilos em `index.html`, e a importação do PhotoSwipe em `assets/app.js`, receberam os novos parâmetros `?v=`. Inclua essas alterações na entrega.
- Preserve as preferências globais de validação no Chrome e uso da instalação compartilhada do Playwright.
- A regra vale para toda alteração de código, HTML, documentação ou configuração do projeto: gere uma nova versão para TODOS os scripts e estilos locais referenciados, mesmo que seus conteúdos permaneçam iguais.
- Compare os parâmetros `?v=` antes e depois da execução com `--force`; todos devem mudar, incluindo o módulo PhotoSwipe importado. Não entregue nem publique a alteração com versões antigas.
