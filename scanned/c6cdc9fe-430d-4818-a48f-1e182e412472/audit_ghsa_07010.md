# [H] Open WebUI: Stored web worker XSS via Pyodide

## Summary
Severity: High
Advisory: GHSA-4r2p-27mh-5m22
CVE: CVE-2026-59214
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-4r2p-27mh-5m22
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.10.0

## Details
**Title:** Same-origin Pyodide code execution allows server-side RCE via a shared chat

### Summary

Open WebUI runs client-side Python (Pyodide) in a same-origin web worker. Through Pyodide's JavaScript API (`pyodide.http.pyfetch`, or the `js` module which exposes the page's `fetch` / `XMLHttpRequest`) executed Python can issue requests on the application origin, and those requests carry the victim's session cookie. A low-privileged user can store such a payload in a chat message, share the chat, and when a victim opens it and clicks **Run** the payload executes authenticated same-origin requests as the victim. When the victim is an admin (or a user holding `workspace.functions` / `workspace.tools` permissions) the payload creates a Function/Tool whose body runs server-side, yielding **remote code execution**.

### Details

Pyodide's `js` bridge gives Python in the worker the same reach as inline JavaScript on the origin, and the worker is same-origin, so a credentialed request to the app's own API is authenticated as the victim. No separate XSS sink is required: storing the payload in a shared chat and having the victim run it is enough.

```python
from pyodide.http import pyfetch
import json
await pyfetch('/api/v1/functions/create', method='POST', credentials='include',
              headers={'Content-Type': 'application/json'},
              body=json.dumps({'id': 'x', 'name': 'x', 'meta': {'description': 'x'},
                               'content': "import os; os.system('<attacker command>')"}))
```

### Impact

When the victim runs the shared code, an authenticated low-privileged user achieves remote code execution on the server (the created Function/Tool runs server-side Python) if the victim is an admin or holds `workspace.functions` / `workspace.tools` permissions. More generally the executed code can issue any authenticated request as the victim. Requires the victim to click Run, and Open WebUI configured to use Pyodide.

### Patched

Pyodide now runs in a sandboxed iframe at an opaque origin by default (`sandbox="allow-scripts"`, no `allow-same-origin`). At an opaque origin `pyfetch`, `fetch` and `XMLHttpRequest` to the app become cross-origin requests that carry no session cookie and are CORS-blocked, and the `js` bridge operates on the isolated iframe window with no access to the parent's cookie, token, `localStorage` or DOM. Full Python, JavaScript and external fetch keep working. IDBFS persistence is available only behind `ENABLE_PYODIDE_FILE_PERSISTENCE=true`, which restores the same-origin worker and re-accepts this risk.

### Workaround

Until upgraded, disable Pyodide code execution or set the Code Execution / Code Interpreter engine to a server-side option.

### Credits

@gg0h

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4r2p-27mh-5m22
- https://nvd.nist.gov/vuln/detail/CVE-2026-59214
- https://github.com/open-webui/open-webui
