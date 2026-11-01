# Recordações Edna Moreira

Álbum estático para https://coreilabs.github.io/fotosedna/.

As fotos originais permanecem em `assets/gallery`. A página carrega lotes de 40 links e usa lazy loading nativo; o visualizador PhotoSwipe pré-carrega apenas fotos vizinhas. Não há miniaturas geradas nem backend.

Após adicionar ou remover fotos JPG, execute `python scripts/catalog.py` para atualizar o catálogo (somente biblioteca padrão do Python).

Para visualizar localmente: `python -m http.server 8080`, depois abra http://localhost:8080. Para publicar no GitHub Pages, envie os arquivos ao repositório `coreilabs/fotosedna` e configure Pages para servir a raiz da branch utilizada.

O botão “Baixar foto” aponta para o arquivo original. Salvar pelo toque prolongado depende do navegador. Links `#foto=N` abrem fotos específicas; mantenha a ordem do catálogo estável se precisar preservar esses links após atualizar o acervo. A prévia social é sempre a do álbum.

PhotoSwipe 5.4.4 distribuído localmente em `assets/vendor`, sob licença MIT.

Antes de publicar alterações de scripts ou estilos, execute `python scripts/version_assets.py`. O comando atualiza as URLs com hashes do conteúdo para renovar o cache dos visitantes sem desativar o cache das fotos. O catálogo também é revalidado ao abrir a página.

Métricas de compartilhamento enviadas à propriedade GA4 `G-ECFESMQ264`:

- `photo_share_click`: acionamento do botão.
- `share`: a API nativa concluiu sem erro; não confirma entrega ao destinatário.
- `photo_link_copy`: o navegador confirmou a cópia do link; não significa envio.
- `photo_share_cancel`: a API nativa reportou cancelamento (`AbortError`).
- `photo_share_error`: falha na API de compartilhamento ou de cópia. A abertura da janela para copiar manualmente não conta como cópia confirmada.

Todos incluem `content_type=image`, `item_id` (nome estável do arquivo original) e `method` (`native` ou `copy_link`). Para analisar fotos e métodos em relatórios/Explorações, cadastre dimensões personalizadas de escopo de evento para `item_id` e `method` no GA4. Bloqueadores podem impedir a coleta. Os dados começam após a publicação e não são retroativos.
