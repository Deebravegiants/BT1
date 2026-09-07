# [M] NiceGUI Reflected XSS in ui.add_css, ui.add_scss, and ui.add_sass via Style Injection

## Summary
Severity: Medium
Advisory: GHSA-72qc-wxch-74mg
CVE: CVE-2025-66469
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-72qc-wxch-74mg
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.4.0

## Details
### Summary
A Cross-Site Scripting (XSS) vulnerability exists in `ui.add_css`, `ui.add_scss`, and `ui.add_sass` functions in NiceGUI (v3.3.1 and earlier).

These functions allow developers to inject styles dynamically. However, they lack proper sanitization or encoding for the JavaScript context they generate. An attacker can break out of the intended `<style>` or `<script>` tags by injecting closing tags (e.g., `</style>` or `</script>`), allowing for the execution of arbitrary JavaScript.

### Details
The vulnerability stems from how these functions inject content into the DOM using `client.run_javascript` (or `add_head_html` internally) without sufficient escaping for the transport layer.

* **`ui.add_css`**: Injects content into a `<style>` tag. Input containing `</style>` closes the tag prematurely, allowing subsequent HTML/JS injection.
* **`ui.add_scss` / `ui.add_sass`**: These rely on client-side compilation within `<script>` tags. Input containing `</script>` breaks the execution context, allowing XSS.

### PoC
**Scenario:** A developer allows users to customize a theme color via a URL parameter.

```python
from nicegui import ui

@ui.page('/')
def main(color: str = 'blue'):
    # Vulnerable implementation of dynamic theming
    ui.add_css(f'.q-btn {{ background-color: {color} !important; }}')
    ui.button('Click Me')

ui.run(port=8082)
```
**Attack Vector:**
Accessing the following URL executes arbitrary JavaScript:
`http://localhost:8082/?color=red;}</style><img src=x onerror=alert(document.domain)><style>`

### Impact
* **Type:** Reflected XSS
* **Severity:** Moderate 
* **Affected Components:** Applications using `ui.add_css`, `ui.add_scss`, or `ui.add_sass` with untrusted input (e.g., dynamic theming based on user input).

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-72qc-wxch-74mg
- https://nvd.nist.gov/vuln/detail/CVE-2025-66469
- https://github.com/zauberzeug/nicegui/commit/a8fd25b7d5e23afb1952d0f60a1940e18b5f1ca8
- https://github.com/zauberzeug/nicegui
