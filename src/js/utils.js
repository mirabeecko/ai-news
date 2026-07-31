/**
 * AI News — Utility functions
 * Formátování data, relativní čas, filtrování
 */

/**
 * Formátuje ISO datum na český formát
 * @param {string} isoDate - ISO 8601 datum
 * @returns {string} - "31. července 2026"
 */
export function formatDate(isoDate) {
  const months = [
    'ledna', 'února', 'března', 'dubna', 'května', 'června',
    'července', 'srpna', 'září', 'října', 'listopadu', 'prosince'
  ];
  const d = new Date(isoDate);
  return `${d.getDate()}. ${months[d.getMonth()]} ${d.getFullYear()}`;
}

/**
 * Vrací relativní časovou frázi
 * @param {string} isoDate - ISO 8601 datum
 * @returns {string} - "před 2 hodinami", "včera", "před 3 dny"
 */
export function timeAgo(isoDate) {
  const now = new Date();
  const then = new Date(isoDate);
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHrs = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHrs / 24);

  if (diffMin < 1) return 'právě teď';
  if (diffMin < 60) return `před ${diffMin} min`;
  if (diffHrs === 1) return 'před hodinou';
  if (diffHrs < 24) return `před ${diffHrs} hodinami`;
  if (diffDays === 1) return 'včera';
  if (diffDays < 7) return `před ${diffDays} dny`;
  return formatDate(isoDate);
}

/**
 * Vrací CSS třídy pro tag (barvu podle kategorie)
 * @param {string} tag
 * @returns {string}
 */
export function tagClass(tag) {
  const map = {
    'open-source': 'tag-green',
    'benchmark': 'tag-purple',
    'multimodal': 'tag-blue',
    'regulation': 'tag-red',
    'investment': 'tag-amber',
    'infrastructure': 'tag-amber',
    'humanoid': 'tag-cyan',
    'embodied-ai': 'tag-cyan',
    'manufacturing': 'tag-cyan'
  };
  return map[tag] || 'tag-default';
}

/**
 * Formátuje tag label pro zobrazení
 * @param {string} tag
 * @returns {string}
 */
export function tagLabel(tag) {
  const map = {
    'open-source': 'Open Source',
    'embodied-ai': 'Embodied AI'
  };
  return map[tag] || tag.charAt(0).toUpperCase() + tag.slice(1);
}
