#!/usr/bin/env python3
"""
AI News — Daily Update Checker
================================
Denní monitoring AI zdrojů. Sbírá nové články/headliny ze sledovaných webů
a generuje strukturovaný report pro cron agenta.

Výstup: JSON report do stdout + do OUTPUTS/ai-news/YYYY-MM-DD/report.json

Pravidla:
- Před přidáním novinky musí být ověřena minimálně ze 2 nezávislých zdrojů
- Všechny změny se logují do changelog.json
- Nikdy nemažeme stará data, pouze přidáváme

Usage:
    python3 scripts/check-updates.py                    # report mode
    python3 scripts/check-updates.py --sources-only      # only list sources
    python3 scripts/check-updates.py --output-dir <path> # custom output dir
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# === CONFIG ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = PROJECT_ROOT / "scripts" / "sources.json"
NEWS_FILE = PROJECT_ROOT / "src" / "data" / "news.json"
CHANGELOG_FILE = PROJECT_ROOT / "src" / "data" / "changelog.json"
DEFAULT_OUTPUT = Path.home() / "Documents" / "MiLO_WORKSPACE" / "OUTPUTS" / "ai-news"


def load_json(path):
    """Načte JSON soubor. Vrací dict nebo prázdný dict při chybě."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Nelze načíst {path}: {e}", file=sys.stderr)
        return {}


def save_json(path, data):
    """Uloží data jako formátovaný JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"✓ Uloženo: {path}", file=sys.stderr)


def get_existing_ids(news_data):
    """Vrátí set všech existujících ID položek."""
    ids = set()
    for cat in (news_data.get("categories") or {}).values():
        for item in cat.get("items", []):
            ids.add(item.get("id", ""))
    return ids


def get_existing_urls(news_data):
    """Vrátí set všech URL, které už máme ve zdrojích."""
    urls = set()
    for cat in (news_data.get("categories") or {}).values():
        for item in cat.get("items", []):
            for src in item.get("sources", []):
                urls.add(src.get("url", ""))
    return urls


def generate_id(title, date_str):
    """Vygeneruje deterministické ID z titulku a data."""
    raw = f"{title}|{date_str}"
    return hashlib.sha256(raw.encode()).hexdigest()[:36]


def get_last_check_date(changelog_data):
    """Zjistí datum poslední kontroly z changelogu."""
    changes = changelog_data.get("changes", [])
    if changes:
        # Vezmeme poslední change, která je typu "check"
        for change in reversed(changes):
            if change.get("action") in ("check", "checked"):
                return change.get("date", "")
    return None


def generate_summary(news_data):
    """Vygeneruje souhrn aktuálního stavu webu."""
    total = 0
    cats = {}
    for key, cat in (news_data.get("categories") or {}).items():
        count = len(cat.get("items", []))
        cats[key] = {"label": cat.get("label", key), "count": count}
        total += count
    return {
        "total_news": total,
        "categories": cats,
        "last_updated": news_data.get("last_updated", "nikdy"),
        "sources_count": 0,  # bude doplněno
    }


def check_sources(sources_data, news_data):
    """
    Prověří všechny zdroje a vrátí report o potenciálně novém obsahu.
    Toto je "sběrná" fáze — skutečné ověření a rozhodnutí dělá cron agent.
    """
    existing_urls = get_existing_urls(news_data)
    existing_ids = get_existing_ids(news_data)

    sources = sources_data.get("sources", [])
    source_status = []

    for src in sources:
        status = {
            "name": src["name"],
            "url": src["url"],
            "category": src["category"],
            "priority": src["priority"],
            "status": "unchecked",
            "note": "Web scraping vyžaduje browser/agent — spustí cron job",
            "potential_new": 0,
        }
        source_status.append(status)

    return {
        "total_sources": len(sources),
        "sources_checked": 0,
        "sources_with_potential_new": 0,
        "source_status": source_status,
        "existing_news_count": len(existing_ids),
        "existing_urls_count": len(existing_urls),
    }


def generate_report(news_data, changelog_data, sources_data):
    """Vygeneruje kompletní report pro cron agenta."""
    now = datetime.now(timezone.utc).isoformat()

    summary = generate_summary(news_data)
    summary["sources_count"] = len(sources_data.get("sources", []))

    source_check = check_sources(sources_data, news_data)

    # Poslední kontrola
    last_check = get_last_check_date(changelog_data)

    # Seznam všech kategorií a jejich zdrojů
    category_sources = {}
    for src in sources_data.get("sources", []):
        cat = src["category"]
        if cat not in category_sources:
            category_sources[cat] = []
        category_sources[cat].append({"name": src["name"], "url": src["url"], "priority": src["priority"]})

    report = {
        "report_type": "daily_check",
        "generated_at": now,
        "project": "ai-news",
        "site_url": "https://ai-news-six-delta.vercel.app",
        "summary": summary,
        "source_check": source_check,
        "last_check_date": last_check,
        "category_sources": category_sources,
        "instructions": {
            "verification_required": sources_data.get("verification_required", True),
            "min_sources_for_new_entry": sources_data.get("min_sources_for_new_entry", 2),
            "output_files": sources_data.get("output", {}),
        },
        "next_steps": [
            "1. Projdi zdroje v category_sources — použij web_search pro každou kategorii",
            "2. Pro každý potenciální nový článek ověř z druhého nezávislého zdroje (web_search)",
            "3. Pokud je novinka ověřená, přidej ji do src/data/news.json",
            "4. Každou změnu zapiš do src/data/changelog.json",
            "5. Po úpravě dat spusť: cd ai-news && npm run build && git add -A && git commit -m 'Daily update YYYY-MM-DD' && git push",
            "6. Vercel automaticky nasadí novou verzi",
        ],
    }

    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI News Daily Checker")
    parser.add_argument("--sources-only", action="store_true", help="Pouze výpis zdrojů")
    parser.add_argument("--output-dir", type=str, help="Vlastní výstupní adresář")
    args = parser.parse_args()

    # Načtení dat
    sources_data = load_json(SOURCES_FILE)
    news_data = load_json(NEWS_FILE)
    changelog_data = load_json(CHANGELOG_FILE)

    if args.sources_only:
        print(json.dumps(sources_data, ensure_ascii=False, indent=2))
        return

    # Generování reportu
    report = generate_report(news_data, changelog_data, sources_data)

    # Uložení reportu
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT / today
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "report.json"
    save_json(report_path, report)

    # Markdown report pro CEO
    md_report = generate_markdown_report(report)
    md_path = output_dir / "report.md"
    md_path.write_text(md_report, encoding="utf-8")
    print(f"✓ Markdown report: {md_path}", file=sys.stderr)

    # Výstup na stdout pro cron
    print(json.dumps(report, ensure_ascii=False, indent=2))


def generate_markdown_report(report):
    """Vygeneruje Markdown verzi reportu pro CEO."""
    s = report["summary"]
    sc = report["source_check"]

    lines = [
        f"# AI News — Daily Check Report",
        f"**Generováno:** {report['generated_at']}",
        f"**Web:** {report['site_url']}",
        "",
        "## Souhrn",
        f"- **Celkem novinek:** {s['total_news']}",
        f"- **Poslední aktualizace:** {s['last_updated']}",
        f"- **Sledovaných zdrojů:** {sc['total_sources']}",
        "",
        "## Kategorie",
    ]

    for key, cat in s["categories"].items():
        lines.append(f"- **{cat['label']}:** {cat['count']} novinek")

    lines.extend([
        "",
        "## Zdroje ke kontrole",
        "",
        "| Zdroj | Kategorie | Priorita |",
        "|-------|-----------|----------|",
    ])

    for src in report["source_check"]["source_status"]:
        lines.append(f"| {src['name']} | {src['category']} | {src['priority']} |")

    lines.extend([
        "",
        "## Instrukce pro agenta",
        "",
        "1. Projdi zdroje — použij `web_search` pro vyhledání nejnovějších AI novinek",
        "2. Pro každou potenciální novinku ověř z druhého zdroje",
        "3. Přidej ověřené novinky do `src/data/news.json`",
        "4. Zapiš změny do `src/data/changelog.json`",
        "5. Spusť build a push:",
        "   ```bash",
        "   cd /Users/mb/Documents/MiLO_WORKSPACE/ai-news",
        "   npm run build",
        "   git add -A && git commit -m 'Daily update' && git push",
        "   ```",
        "",
        "---",
        f"*Report vygenerován skriptem `scripts/check-updates.py`*",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    main()
