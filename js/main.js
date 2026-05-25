/* ────────────────────────────────────────────────────────────
   phritz – main.js
   ──────────────────────────────────────────────────────────── */

// ── Loader ───────────────────────────────────────────────────
window.addEventListener('load', () => {
  setTimeout(() => document.getElementById('loader').classList.add('hidden'), 600);
});

// ── Floating header: switch color when leaving the hero ───────
const siteHeader = document.getElementById('site-header');
const hero       = document.getElementById('hero');

if (siteHeader && hero) {
  siteHeader.classList.add('on-hero');
  const headerObserver = new IntersectionObserver(
    ([entry]) => {
      siteHeader.classList.toggle('on-hero', entry.isIntersecting);
      // Always reveal header when returning to the hero
      if (entry.isIntersecting) siteHeader.classList.remove('header-hidden');
    },
    { threshold: 0 }
  );
  headerObserver.observe(hero);
}

// ── Hide on scroll-down, reveal on scroll-up ─────────────────
let lastScrollY = window.scrollY;
const SCROLL_DELTA = 8; // px dead-zone to avoid jitter

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (siteHeader && !siteHeader.classList.contains('on-hero')) {
    if (y > lastScrollY + SCROLL_DELTA) {
      siteHeader.classList.add('header-hidden');
    } else if (y < lastScrollY - SCROLL_DELTA) {
      siteHeader.classList.remove('header-hidden');
    }
  }
  lastScrollY = y;
}, { passive: true });

// ── Scroll-based scroll-hint fade ────────────────────────────
const scrollHint = document.querySelector('.scroll-hint');

function onScroll() {
  const s  = window.scrollY;
  const vh = window.innerHeight;
  if (scrollHint) scrollHint.style.opacity = Math.max(0, 1 - s / (vh * 0.22));
}
window.addEventListener('scroll', onScroll, { passive: true });

// ── IntersectionObserver: generic fade-in sections ───────────
const io = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
  }),
  { threshold: 0.08 }
);
document.querySelectorAll('.fade-in').forEach(el => io.observe(el));

// ── Discography: merge Spotify + manual, render + filter ──────
function mergeReleases() {
  const spotify = Array.isArray(window.RELEASES_SPOTIFY) ? window.RELEASES_SPOTIFY : [];
  const manual  = Array.isArray(window.RELEASES_MANUAL)  ? window.RELEASES_MANUAL  : [];

  // Spotify-fetched entries take precedence; deduplicate by Spotify link
  // (also deduplicates within manual entries themselves)
  const seen = new Set(spotify.map(r => r.link));
  const unique = [...spotify];
  for (const r of manual) {
    if (!seen.has(r.link)) {
      seen.add(r.link);
      unique.push(r);
    }
  }

  // Sort newest first — use release_date (from Spotify) when available, else year
  unique.sort((a, b) => {
    const da = a.release_date || `${a.year}-12-31`;
    const db = b.release_date || `${b.year}-12-31`;
    return db.localeCompare(da);
  });

  return unique;
}

function buildGrid(releases) {
  const grid = document.getElementById('releases-grid');
  if (!grid) return;

  const LIMIT = 10;

  // Remove any existing show-more button from a previous filter/call
  const existing = document.getElementById('disco-show-more');
  if (existing) existing.remove();

  grid.innerHTML = releases.map((r, i) => `
    <a
      class="release-tile${i >= LIMIT ? ' tile-folded' : ''}"
      href="${r.link}"
      target="_blank"
      rel="noopener noreferrer"
      data-project="${r.project}"
      style="transition-delay:${(i % 10) * 35}ms"
    >
      <img src="${r.artwork}" alt="${r.title}" loading="lazy" decoding="async">
      <div class="release-overlay">
        <p class="release-title">${r.title}</p>
        <p class="release-meta">${r.project} · ${r.year}</p>
      </div>
    </a>
  `).join('');

  // Stagger tile entrance (visible tiles only)
  const tileIO = new IntersectionObserver(
    (entries) => entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('tile-visible'); tileIO.unobserve(e.target); }
    }),
    { threshold: 0.04, rootMargin: '0px 0px -30px 0px' }
  );

  const observeVisible = () => {
    grid.querySelectorAll('.release-tile:not(.tile-folded):not(.tile-visible)').forEach(t => tileIO.observe(t));
  };
  observeVisible();

  // Toggle button: show all ↔ show less
  if (releases.length > LIMIT) {
    const btn = document.createElement('button');
    btn.id = 'disco-show-more';
    btn.className = 'show-more-btn';

    const collapse = () => {
      Array.from(grid.querySelectorAll('.release-tile')).slice(LIMIT).forEach(t => {
        t.classList.add('tile-folded');
        t.classList.remove('tile-visible');
      });
      btn.textContent = `show all (${releases.length})`;
      btn.onclick = expand;
      grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const expand = () => {
      grid.querySelectorAll('.tile-folded').forEach(t => t.classList.remove('tile-folded'));
      observeVisible();
      btn.textContent = 'show less';
      btn.onclick = collapse;
    };

    btn.textContent = `show all (${releases.length})`;
    btn.onclick = expand;
    grid.insertAdjacentElement('afterend', btn);
  }
}

function initDiscography() {
  const releases = mergeReleases();
  if (releases.length === 0) return;

  // Build filter tabs (only for projects with at least one release)
  const filterBar = document.getElementById('filter-bar');
  let activeProject = 'all';

  if (filterBar) {
    const PROJECT_ORDER = ['phritz', 'tai hirose', 'tiny pool centennial'];
    const usedProjects = [...new Set(releases.map(r => r.project))];
    usedProjects.sort((a, b) => {
      const ai = PROJECT_ORDER.indexOf(a);
      const bi = PROJECT_ORDER.indexOf(b);
      return (ai < 0 ? 99 : ai) - (bi < 0 ? 99 : bi);
    });
    const labels = ['all', ...usedProjects];
    const btns = labels.map((label, i) => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn' + (i === 0 ? ' active' : '');
      btn.dataset.project = label;
      btn.textContent = label;
      return btn;
    });
    btns.forEach(b => filterBar.appendChild(b));

    filterBar.addEventListener('click', e => {
      const btn = e.target.closest('.filter-btn');
      if (!btn) return;
      activeProject = btn.dataset.project;
      btns.forEach(b => b.classList.toggle('active', b === btn));
      const filtered = activeProject === 'all'
        ? releases
        : releases.filter(r => r.project === activeProject);
      buildGrid(filtered);
    });
  }

  buildGrid(releases);
}

initDiscography();

// ── Other Works: fold excess items behind show-more ───────────
function initOtherWorks() {
  const grid = document.getElementById('works-grid');
  if (!grid) return;

  const LIMIT = 8;
  const items = Array.from(grid.querySelectorAll('.work-item'));
  if (items.length <= LIMIT) return;

  items.slice(LIMIT).forEach(item => item.classList.add('work-hidden'));

  const btn = document.createElement('button');
  btn.className = 'show-more-btn';

  const collapseWorks = () => {
    items.slice(LIMIT).forEach(item => item.classList.add('work-hidden'));
    btn.textContent = `show all (${items.length})`;
    btn.onclick = expandWorks;
    grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const expandWorks = () => {
    items.forEach(item => item.classList.remove('work-hidden'));
    btn.textContent = 'show less';
    btn.onclick = collapseWorks;
  };

  btn.textContent = `show all (${items.length})`;
  btn.onclick = expandWorks;
  grid.insertAdjacentElement('afterend', btn);
}

initOtherWorks();

// ── Clients / Live tab switcher ───────────────────────────────
const clTabs   = document.querySelectorAll('.cl-tab');
const clPanels = document.querySelectorAll('.cl-panel');

clTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.panel;
    clTabs.forEach(t   => t.classList.toggle('active', t === tab));
    clPanels.forEach(p => p.classList.toggle('cl-panel--hidden', p.id !== `panel-${target}`));
  });
});

// ── Slide-in social menu (mobile/tablet) ─────────────────────
const menuToggle  = document.getElementById('menu-toggle');
const socialMenu  = document.getElementById('social-menu');
const menuOverlay = document.getElementById('menu-overlay');
const menuClose   = document.getElementById('menu-close');

function openSocialMenu() {
  socialMenu.classList.add('open');
  menuOverlay.classList.add('open');
  menuToggle.setAttribute('aria-expanded', 'true');
  socialMenu.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeSocialMenu() {
  socialMenu.classList.remove('open');
  menuOverlay.classList.remove('open');
  menuToggle.setAttribute('aria-expanded', 'false');
  socialMenu.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

if (menuToggle)  menuToggle.addEventListener('click', openSocialMenu);
if (menuClose)   menuClose.addEventListener('click', closeSocialMenu);
if (menuOverlay) menuOverlay.addEventListener('click', closeSocialMenu);

document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && socialMenu?.classList.contains('open')) closeSocialMenu();
});
