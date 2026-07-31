/**
 * AI News — Renderer
 * Dynamické renderování HTML z news.json
 */
import { formatDate, timeAgo, tagClass, tagLabel } from './utils.js';

/**
 * Zobrazí loading stav
 */
export function renderLoading() {
  const main = document.getElementById('news-container');
  main.innerHTML = `
    <div class="loading-state">
      <div class="loading-pulse"></div>
      <p class="loading-text">Načítám data...</p>
    </div>`;
}

/**
 * Zobrazí chybový stav
 * @param {string} message
 */
export function renderError(message) {
  const main = document.getElementById('news-container');
  main.innerHTML = `
    <div class="error-state">
      <span class="error-icon">⚠️</span>
      <p class="error-text">${message || 'Data se nepodařilo načíst.'}</p>
    </div>`;
}

/**
 * Renderuje jednu novinkovou kartu
 * @param {object} item
 * @param {string} category
 * @returns {string} HTML
 */
function renderNewsCard(item, category) {
  const sourceLinks = item.sources
    .map(s => `<a href="${s.url}" target="_blank" rel="noopener" class="source-link">${s.label}</a>`)
    .join('<span class="source-sep">·</span>');

  const tags = (item.tags || [])
    .map(t => `<span class="tag ${tagClass(t)}">${tagLabel(t)}</span>`)
    .join('');

  const verifiedBadge = item.verified
    ? `<span class="verified-badge" title="Ověřeno z ${item.sources_checked || 2} zdrojů">✓ ${item.verification_source || 'Ověřeno'}</span>`
    : '';

  return `
    <article class="news-card" data-category="${category}" data-id="${item.id}">
      <div class="news-card-header">
        <time class="news-date" datetime="${item.date}">${timeAgo(item.date)}</time>
        <div class="news-meta">
          ${verifiedBadge}
          ${tags}
        </div>
      </div>
      <h3 class="news-title">${escapeHtml(item.title)}</h3>
      <p class="news-summary">${escapeHtml(item.summary)}</p>
      <div class="news-sources">
        <span class="sources-label">Zdroje:</span>
        ${sourceLinks}
      </div>
    </article>`;
}

/**
 * Renderuje celou sekci kategorie
 * @param {string} key - klíč kategorie (modely, plany, robotika)
 * @param {object} category - data kategorie
 * @returns {string} HTML
 */
function renderCategory(key, category) {
  const items = category.items || [];
  if (items.length === 0) {
    return `
      <section class="category-section" id="cat-${key}">
        <div class="category-header">
          <span class="category-icon">${category.icon || ''}</span>
          <h2 class="category-title">${escapeHtml(category.label)}</h2>
        </div>
        <p class="category-desc">${escapeHtml(category.description)}</p>
        <div class="empty-state">
          <p>Zatím žádné novinky v této kategorii.</p>
        </div>
      </section>`;
  }

  const cards = items
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .map(item => renderNewsCard(item, key))
    .join('');

  return `
    <section class="category-section" id="cat-${key}">
      <div class="category-header">
        <span class="category-icon">${category.icon || ''}</span>
        <h2 class="category-title">${escapeHtml(category.label)}</h2>
        <span class="category-count">${items.length} novinek</span>
      </div>
      <p class="category-desc">${escapeHtml(category.description)}</p>
      <div class="news-grid">
        ${cards}
      </div>
    </section>`;
}

/**
 * Hlavní renderovací funkce — vykreslí celou stránku
 * @param {object} data - data z news.json
 */
export function renderPage(data) {
  const container = document.getElementById('news-container');
  const lastUpdated = document.getElementById('last-updated-time');

  if (!data || !data.categories) {
    renderError('Neplatná data.');
    return;
  }

  // Last updated timestamp
  if (lastUpdated && data.last_updated) {
    lastUpdated.textContent = formatDate(data.last_updated);
    lastUpdated.setAttribute('datetime', data.last_updated);
  }

  // Category tabs
  const tabs = document.getElementById('category-tabs');
  if (tabs) {
    tabs.innerHTML = Object.entries(data.categories)
      .map(([key, cat]) => `
        <button class="cat-tab active" data-cat="${key}" onclick="window._switchTab('${key}')">
          ${cat.icon || ''} ${escapeHtml(cat.label)}
        </button>`)
      .join('');
  }

  // Render all categories
  const sections = Object.entries(data.categories)
    .map(([key, cat]) => renderCategory(key, cat))
    .join('');

  container.innerHTML = sections;

  // First tab interaction
  const firstTab = document.querySelector('.cat-tab');
  if (firstTab) firstTab.classList.add('active');
}

/**
 * Přepne viditelnost kategorií podle vybraného tabu
 * @param {string} activeCat
 */
export function switchTab(activeCat) {
  document.querySelectorAll('.cat-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.cat === activeCat);
  });
  document.querySelectorAll('.category-section').forEach(section => {
    section.classList.toggle('hidden', section.id !== `cat-${activeCat}`);
  });
}

/**
 * Escapuje HTML entity
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
