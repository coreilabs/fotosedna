# Álbum de Fotos de Edna Moreira

Álbum estático para https://coreilabs.github.io/fotosedna/.

## Conversão local em lotes

Requisitos: Python e ImageMagick (`magick` no PATH), já instalados nesta máquina. Não requer Codex, API nem créditos. Qualidade padrão 82, sem redimensionamento; aplica orientação EXIF e remove metadados da cópia WebP.

Clique duas vezes em `converter-fotos.bat` para processar o próximo lote de 100 fotos, ou execute:

```powershell
# Um lote de 100; repetir retoma o progresso.
python scripts/convert_webp.py

# Todos os lotes restantes, preservando JPGs.
python scripts/convert_webp.py --all --batch-size 100 --workers 4

# Todos os lotes, com exclusão dos JPGs após validar TODOS os WebP.
python scripts/convert_webp.py --all --batch-size 100 --workers 4 --delete-originals

# Apenas validar conversões prontas e excluir os JPGs correspondentes.
python scripts/verify_webp.py --delete-originals

# Máquina mais limitada: lote de 25, uma conversão por vez.
python scripts/convert_webp.py --batch-size 25 --workers 1
```

Novos JPGs devem ser colocados em `assets/gallery`. O resultado fica em `assets/gallery-webp`. O progresso é salvo ao final de cada lote em `scripts/webp-progress.json`; arquivos já convertidos e inalterados são pulados. Falhas são informadas e tentadas novamente na próxima execução. `--quality 85` altera a qualidade dos JPGs ainda disponíveis. A conversão tem perdas; apagar os JPGs é uma ação explícita e irreversível sem backup.

Não execute duas instâncias simultâneas. Após encerramento forçado, remova `scripts/webp-conversion.lock` apenas depois de confirmar que o processo terminou. Ao final, o helper atualiza automaticamente o catálogo e força novas versões do CSS/JS. Publique os WebP, as exclusões dos JPGs, o catálogo e os arquivos versionados juntos.

O verificador decodifica todos os WebP correspondentes antes de excluir qualquer JPG, confere o registro de conversão e restringe a exclusão aos caminhos exatos dos originais deste projeto.

## Galeria

Grade, visualizador e download usam WebP; durante a conversão parcial há fallback para JPG. A conversão mantém a ordem do catálogo e os IDs das métricas. O catálogo funciona somente com WebP, mesmo sem JPGs ou registro de progresso.

A grade virtualiza blocos de 40 fotos, mantendo elementos apenas próximos da tela ou com foco de teclado. Limita downloads a quatro, priorizando a região visível e uma margem de 200 px; requisições distantes são abortadas. O PhotoSwipe pré-carrega apenas fotos vizinhas. Não há miniaturas nem backend. A liberação de memória e o cache dependem do navegador.

Após remover ou adicionar arquivos manualmente: `python scripts/catalog.py`. Links `#foto=N` abrem fotos específicas; adições e remoções podem alterar esses índices. A prévia social é sempre a do álbum.

## Visualização e publicação

Execute `python -m http.server 8080` e abra http://localhost:8080. Publique a raiz do repositório `coreilabs/fotosedna` no GitHub Pages.

Antes de entregar qualquer modificação: `python scripts/version_assets.py --force`. Novas versões são geradas mesmo sem mudanças no conteúdo. O catálogo é revalidado ao abrir a página.

PhotoSwipe 5.4.4 distribuído localmente em `assets/vendor`, sob licença MIT.

## Métricas GA4

Propriedade `G-ECFESMQ264`:

- `photo_share_click`: acionamento do botão.
- `share`: API nativa concluída; não confirma entrega.
- `photo_link_copy`: cópia do link confirmada; não significa envio.
- `photo_share_cancel`: cancelamento reportado pela API (`AbortError`).
- `photo_share_error`: falha de compartilhamento ou cópia. A janela de cópia manual não conta como cópia confirmada.

Parâmetros: `content_type=image`, `item_id` (nome original estável, mantido após converter) e `method` (`native` ou `copy_link`). Para analisar fotos e métodos, cadastre dimensões personalizadas de escopo de evento para `item_id` e `method` no GA4. Bloqueadores podem impedir a coleta. Os dados começam após publicar e não são retroativos.

### Rastreamento das interações

A função central `track()` envia os eventos com `album_id=fotosedna`. `trackPhoto()` acrescenta `content_type=image`, `item_id` (arquivo original estável) e `photo_number` (posição atual no catálogo).

- `photo_open`: uma abertura do visualizador, com `origin=gallery` ou `direct_link`.
- `photo_view`: foto selecionada na abertura e a cada mudança por botão, teclado, gesto ou hash. Usa `origin=viewer` nas mudanças internas; imagens pré-carregadas não contam.
- `photo_download_click`: clique em baixar, com `file_name`; não comprova gravação no dispositivo.
- Eventos de compartilhamento anteriores preservados, com os mesmos parâmetros de foto e álbum.
- `navigation_click`: link para outra página, inclusive do mesmo domínio, com `link_name`, `link_url` e `link_domain`.
- `ui_action`: `action=next_photo`, `previous_photo`, `toggle_zoom`, `close_photo`, `load_more` ou `anchor_navigation`. Fechar conta também por teclado/gesto. `load_more` registra apenas acionamento explícito, com `photos_shown`; carregamento automático não conta como clique.

Um clique no ícone dentro de um controle não duplica seu evento. Uma interação pode produzir eventos de intenção e resultado, como `ui_action` ao avançar e `photo_view` para a foto selecionada; não some todos como cliques. Áreas sem ação não geram evento. Bloqueadores e falta de conexão podem impedir coleta.

No GA4, cadastre dimensões personalizadas de **escopo de evento** para `album_id`, `item_id`, `origin`, `action` e `method`. Para analisar `photo_number` e `photos_shown` numericamente, cadastre métricas personalizadas. Use dimensões nativas de link/arquivo quando disponíveis; cadastre `link_name` se quiser esse rótulo. Monte Explorações com evento e foto nas linhas e contagem de eventos/usuários nos valores. Muitos arquivos distintos podem gerar agrupamento em `(other)`; considere BigQuery para volumes elevados.

Medição otimizada pode coletar eventos automáticos adicionais. Filtre `photo_download_click` e `navigation_click` nos rankings, sem somar `file_download`/`click`. O código não altera configurações da propriedade GA4. Valide parâmetros no DebugView com depuração habilitada na sessão de teste. A coleta começa na versão publicada e não é retroativa.
