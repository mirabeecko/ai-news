# AI News — Forever Actual

Odborný web přinášející novinky ze světa AI — modely, plány, robotika. Pro každého, kdo chce mít aktuální informace a nikdy nebýt late.

## Co sledujeme

- **🧠 AI Modely** — nové modely, benchmarky, fine-tuny, open-source releases
- **📋 AI Plány & Strategie** — roadmapy, korporátní oznámení, regulace, investice
- **🤖 AI Robotika** — humanoidi, autonomní systémy, embodied AI, průmyslová robotika

## Principy

1. **Dvouzdrojová verifikace** — každá novinka ověřena minimálně ze dvou nezávislých zdrojů
2. **Denní aktualizace** — automatický cron monitoring zdrojových webů
3. **Transparentnost** — všechny změny zaznamenány v `changelog.json`

## Tech stack

- HTML5 + Vanilla JS (ES modules) + Tailwind CSS 4
- Statický web, data v JSON (`news.json` + `changelog.json`)
- Hosting: Vercel (autodeploy z `main` větve)
- Automatizace: Hermes cron job (denní kontrola a aktualizace)

## Struktura

```
ai-news/
├── index.html              # Hlavní stránka
├── src/
│   ├── css/tailwind.css    # Tailwind vstup
│   ├── js/
│   │   ├── app.js          # Inicializace
│   │   ├── renderer.js     # Renderování z JSON
│   │   └── utils.js        # Pomocné funkce
│   └── data/
│       ├── news.json       # Veškerý obsah webu
│       └── changelog.json  # Historie změn
├── web/                    # Build output (Vercel root)
├── package.json
├── vercel.json
└── .vercelignore
```

## Lokální vývoj

```bash
npm install
npm run dev      # http://localhost:8082
```

## Build & Deploy

```bash
npm run build    # Tailwind CSS + copy to web/
git push         # Vercel autodeploy
```
