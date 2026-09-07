# [M] NiceGUI apps are vulnerable to XSS which uses `ui.sub_pages` and render arbitrary user-provided links

## Summary
Severity: Medium
Advisory: GHSA-m7j5-rq9j-6jj9
CVE: CVE-2026-21872
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-m7j5-rq9j-6jj9
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=2.22.0 <3.5.0

## Details
### Summary

An unsafe implementation in the `click` event listener used by `ui.sub_pages`, combined with attacker-controlled link rendering on the page, causes an XSS when the user actively clicks on the link. 

### Details

1. On `click`, eventually `sub_pages_navigate` event is emitted.
https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/elements/sub_pages.js#L41-L63

2. SubPagesRouter (used by ui.sub_pages), lisnening on `sub_pages_navigate`, `_handle_navigate` runs.
https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/sub_pages_router.py#L18-L22

3. `_handle_navigate` runs `run_javascript` with f-string substituting `self.current_path` which is simply surrounded by double-quotes. The string context can be broken out easily. 

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/sub_pages_router.py#L73-L88

### PoC

The minimal PoC boils down to this:

```py
from nicegui import ui

ui.sub_pages({'/': lambda: ui.link('Go to XSS', '/"+alert(1)+"')})

ui.run()
```

However, it is more likely that the attack takes place with attacker-controlled input, for which this shows it:

```py
from nicegui import app, ui

ui.sub_pages({'/': lambda: ui.label('Hello, World!')})

ui.textarea('Markdown content').bind_value(app.storage.general, 'markdown_content')

ui.markdown().bind_content_from(app.storage.general, 'markdown_content')

ui.run()
```

Vulnerable input is `[XSS LINK](/"+alert(document.domain)+")` (causes double payload execution, though)

**Both cases require someone to click on the link.** 

<img width="1428" height="254" alt="image" src="https://github.com/user-attachments/assets/8be4f345-c0cf-4df2-9917-677a2ea72626" />

### Impact

Any page which uses `ui.sub_pages` and renders arbitrary links on screen (common case of `ui.markdown`) is affected.

The impact is low since a click is always required from the user, who can on-hover to discover the sketchy content of the link and stop if well-trained. 

### Appendix

AI is used safely to judge the CVSS scoring (input is not even provided, just the impact statement).

Please find the results in https://poe.com/s/y5DvyqgtszDGLUuHin1O

### Scoring update after manual review

- Scope **Changed** is more inline with other posted XSS vulnerabilities
- Availability **None**: No DDoS is possible with this. Site remains performant as ever.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-m7j5-rq9j-6jj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-21872
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.5.0
