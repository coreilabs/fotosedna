import PhotoSwipe from './vendor/photoswipe.esm.min.js?v=542069771beb';

const gallery = document.querySelector('#gallery');
const status = document.querySelector('#status');
const more = document.querySelector('#load-more');
const progress = document.querySelector('#progress');
let photos = [], shown = 0, viewer, trigger;
const number = value => value.toLocaleString('pt-BR');
const source = index => `assets/gallery/${encodeURIComponent(photos[index].file)}`;
const photoIndex = () => {
  const match = location.hash.match(/^#foto=(\d+)$/);
  return match ? Number(match[1]) - 1 : -1;
};

function trackPhotoShare(event, photo, method) {
  // Analytics failures must never interrupt sharing.
  try {
    window.gtag?.('event', event, {
      send_to: 'G-ECFESMQ264',
      content_type: 'image',
      item_id: photo.file,
      method,
    });
  } catch { /* Keep sharing available when analytics is blocked. */ }
}

async function sharePhoto(index, label) {
  const photo = photos[index];
  const url = new URL(location.href); url.hash = `foto=${index + 1}`;
  const method = typeof navigator.share === 'function' ? 'native' : 'copy_link';
  trackPhotoShare('photo_share_click', photo, method);
  try {
    if (method === 'native') {
      await navigator.share({ title: 'Álbum de Fotos de Edna Moreira', url: url.href });
      // Browser completion does not prove delivery to a recipient.
      trackPhotoShare('share', photo, method);
    } else {
      await navigator.clipboard.writeText(url.href);
      trackPhotoShare('photo_link_copy', photo, method);
      label.textContent = 'Link copiado!';
      setTimeout(() => { label.textContent = 'Compartilhar'; }, 2000);
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      trackPhotoShare('photo_share_cancel', photo, method);
    } else {
      trackPhotoShare('photo_share_error', photo, method);
      window.prompt('Copie o link desta recordação:', url.href);
      // Opening a copy prompt is not evidence that the link was copied.
    }
  }
}

function addBatch() {
  const end = Math.min(shown + 40, photos.length);
  const fragment = document.createDocumentFragment();
  for (let i = shown; i < end; i++) {
    const link = document.createElement('a');
    link.className = 'photo'; link.href = source(i); link.dataset.index = i;
    link.setAttribute('aria-label', `Ampliar foto ${i + 1}`);
    const img = document.createElement('img');
    img.src = source(i); img.alt = `Recordação de Edna Moreira — foto ${i + 1}`;
    img.width = photos[i].width; img.height = photos[i].height;
    img.loading = 'lazy'; img.decoding = 'async';
    img.addEventListener('error', () => link.classList.add('failed'), { once: true });
    link.append(img); fragment.append(link);
  }
  gallery.append(fragment); shown = end;
  more.hidden = shown >= photos.length;
  progress.textContent = `${number(shown)} de ${number(photos.length)} recordações`;
}

function openPhoto(index, origin) {
  if (index < 0 || index >= photos.length || viewer) return;
  trigger = origin || document.activeElement;
  viewer = new PhotoSwipe({
    dataSource: photos.map((photo, i) => ({ src: source(i), width: photo.width, height: photo.height, alt: `Recordação de Edna Moreira — foto ${i + 1}` })),
    index, preload: [1, 1], loop: false, bgOpacity: .97,
    paddingFn: viewport => ({ top: 64, bottom: viewport.x <= 700 ? 96 : 100, left: 0, right: 0 }),
    closeTitle: 'Fechar', zoomTitle: 'Ampliar', arrowPrevTitle: 'Foto anterior', arrowNextTitle: 'Próxima foto',
    errorMsg: 'Não foi possível carregar esta foto. Feche e tente novamente.',
    returnFocus: false,
  });
  viewer.on('uiRegister', () => {
    viewer.ui.registerElement({ name: 'actions', appendTo: 'root', order: 7, isButton: false,
      onInit: (element, pswp) => {
        element.setAttribute('role', 'group');
        element.setAttribute('aria-label', 'Ações da foto');
        const download = document.createElement('a');
        download.className = 'photo-action photo-action--download';
        download.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg><span>Baixar foto</span>';
        download.setAttribute('aria-label', 'Baixar foto original');
        pswp.on('change', () => { download.href = source(pswp.currIndex); download.download = photos[pswp.currIndex].file; });
        const share = document.createElement('button');
        share.type = 'button'; share.className = 'photo-action photo-action--share';
        share.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.5 6.8-4m-6.8 7 6.8 4"/></svg><span>Compartilhar</span>';
        const label = share.querySelector('span');
        label.setAttribute('aria-live', 'polite');
        let sharing = false;
        share.onclick = async () => {
          if (sharing) return;
          sharing = true;
          try {
            await sharePhoto(pswp.currIndex, label);
          } finally { sharing = false; }
        };
        element.append(download, share);
      }
    });
  });
  viewer.on('change', () => history.replaceState(null, '', `#foto=${viewer.currIndex + 1}`));
  viewer.on('destroy', () => { viewer = undefined; if (photoIndex() >= 0) history.replaceState(null, '', location.pathname + location.search + '#album'); trigger?.focus({ preventScroll: true }); });
  viewer.init();
}

gallery.addEventListener('click', event => {
  const link = event.target.closest('a[data-index]');
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault(); openPhoto(Number(link.dataset.index), link);
});
more.addEventListener('click', addBatch);
window.addEventListener('hashchange', () => {
  const index = photoIndex();
  if (index >= 0 && index < photos.length) { if (viewer) viewer.goTo(index); else openPhoto(index); }
  else viewer?.close();
});

async function load() {
  try {
    const response = await fetch('assets/photos.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error('Catalog unavailable');
    photos = await response.json();
    document.querySelector('#total').textContent = number(photos.length);
    status.hidden = true; addBatch();
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        if (entries.some(entry => entry.isIntersecting) && !more.hidden && !viewer) addBatch();
      }, { rootMargin: '350px' });
      observer.observe(more);
    }
    openPhoto(photoIndex());
  } catch {
    status.textContent = 'Não foi possível carregar o álbum. ';
    const retry = document.createElement('button'); retry.textContent = 'Tentar novamente';
    retry.onclick = () => { status.textContent = 'Preparando as recordações…'; load(); };
    status.append(retry);
  }
}
load();
