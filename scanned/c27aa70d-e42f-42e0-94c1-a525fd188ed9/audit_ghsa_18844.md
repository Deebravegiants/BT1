# [M] NiceGUI has a Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-8c95-hpq2-w46f
CVE: CVE-2025-53354
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-03
Source: https://github.com/advisories/GHSA-8c95-hpq2-w46f
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.0.0

## Details
### Summary

A Cross-Site Scripting (XSS) risk exists in NiceGUI when developers render unescaped user input into the DOM using `ui.html()`. Before version 3.0, NiceGUI does not enforce HTML or JavaScript sanitization, so applications that directly combine components like `ui.input()` with `ui.html()` without escaping may allow attackers to execute arbitrary JavaScript in the user’s browser. Same holds for `ui.chat_message` with HTML content.

Applications that directly reflect user input via `ui.html()` (or `ui.chat_message` in HTML mode) are affected. This may lead to client-side code execution (e.g., session hijacking or phishing). Applications that do not pass untrusted input into ui.html() are not affected.

### Details

NiceGUI allows developers to bind user input directly into the DOM using `ui.html()` or `ui.chat_message()`. However, the library does not enforce any HTML or JavaScript sanitization, which potentially creates a dangerous attack surface for developers unaware of this behavior.

The vulnerable code path appears when combining these:

```python
ui.input("XSS Input:", on_change=inject)
def inject(e):
    ui.html(f'{e.value}')
```

In this setup, any input provided by the user is rendered **verbatim** into the page’s DOM via innerHTML, enabling injection of script-based payloads.

### PoC (Proof of Concept)

1. Create a simple app:

   ```python
   from nicegui import ui

   @ui.page('/')
   def main():
       def inject(e):
           ui.html(f'{e.value}')  # vulnerable use

       ui.input("XSS Input:", on_change=inject)

   ui.run()
   ```

2. Run the app:

   ```bash
   python app.py
   ```

3. In the browser, input the following payload:

   ```html
   <img src=x onerror=alert('XSS')>
   ```

4. Observe the JavaScript alert popup:

   ```
   XSS
   ```

### Impact

* **Vulnerability type:** Reflected Cross-Site Scripting (XSS)
* **Attack vector:** User input rendered as raw HTML
* **Affected users:** Any NiceGUI-based application using `ui.html()` or `ui.chat_message()` with HTML content from user input

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-8c95-hpq2-w46f
- https://nvd.nist.gov/vuln/detail/CVE-2025-53354
- https://github.com/zauberzeug/nicegui/commit/4673dc35c94a0c7339e2164378b0977332e60775
- https://github.com/zauberzeug/nicegui
