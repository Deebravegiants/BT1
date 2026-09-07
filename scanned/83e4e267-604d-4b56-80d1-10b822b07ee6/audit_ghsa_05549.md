# [M] NiceGUI is vulnerable to XSS via Unescaped URL in ui.navigate.history.push() / replace()

## Summary
Severity: Medium
Advisory: GHSA-7grm-h62g-5m97
CVE: CVE-2026-21871
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-7grm-h62g-5m97
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=2.13.0 <3.5.0

## Details
### Summary
XSS risk exists in NiceGUI when developers pass attacker-controlled strings into `ui.navigate.history.push()` or `ui.navigate.history.replace()`. These helpers are documented as History API wrappers for updating the browser URL without page reload. However, if the URL argument is embedded into generated JavaScript without proper escaping, a crafted payload can break out of the intended string context and execute arbitrary JavaScript in the victim’s browser.

**Applications that do not pass untrusted input into `ui.navigate.history.push/replace` are not affected.**

### Details
NiceGUI provides `ui.navigate.history.push(url)` and `ui.navigate.history.replace(url)` to update the URL using the browser History API. If an application forwards user-controlled data (e.g., URL path segments, query parameters like `next=...`, form values, etc.) into these methods, an attacker can inject characters such as quotes and statement terminators to escape the JavaScript string context and execute arbitrary code.

A vulnerable pattern is:
- attacker controls a value (e.g., via the request path),
- the application passes it to `ui.navigate.history.push(payload)` (or `replace`).

This is similar in spirit to other NiceGUI XSS advisories:
- `ui.html()`,`ui.chat_message()` can cause XSS when developers render untrusted input as HTML (XSS risk/footgun).
- `ui.interactive_image` had XSS via unsanitized SVG content and was handled as a security advisory with a fix and severity rating.

Because `ui.navigate.history.*` is expected to accept a URL (data) rather than executable code, the library should escape/encode the argument before emitting JavaScript.

### PoC
#### Create a simple app

```python
from nicegui import ui

@ui.page('/')
def index():
    # A link/button a victim could click (attacker can also send the URL directly)
    ui.button('open crafted path', on_click=lambda: ui.navigate.to('/%22);alert(document.domain);//'))

@ui.page('/{payload:path}')
def victim(payload: str):
    ui.label(f'payload = {payload!r}')

    # Vulnerable use: forwarding attacker-controlled path to history.push
    ui.button('trigger', on_click=lambda: ui.navigate.history.push(payload))

ui.run()
```

#### Run the app

```bash
python app.py
```

#### Trigger

1. Open `http://localhost:8080/`
2. Click `open crafted path`
3. Click `trigger`

Expected result: JavaScript executes (an alert showing `document.domain`).

### Impact
- Vulnerability type: DOM-based XSS
- Attack vector: attacker-controlled input embedded into JavaScript via `ui.navigate.history.push/replace`
- Affected users: any NiceGUI-based application that forwards untrusted input into `ui.navigate.history.push()` or `ui.navigate.history.replace()`
- Potential outcomes: client-side code execution, phishing UI injection, and other typical XSS impacts

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-7grm-h62g-5m97
- https://nvd.nist.gov/vuln/detail/CVE-2026-21871
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.5.0
