/**
 * AI News — Main Application
 * Inicializace, načtení dat, event handling
 */
import { renderPage, renderLoading, renderError, switchTab } from './renderer.js';

// Expose switchTab globally for onclick handlers
window._switchTab = switchTab;

/**
 * Načte news.json a vyrenderuje stránku
 */
async function init() {
  renderLoading();

  try {
    const response = await fetch('/src/data/news.json');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    renderPage(data);
  } catch (err) {
    console.error('Failed to load news data:', err);
    renderError('Data se nepodařilo načíst. Zkontrolujte připojení.');
  }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
