# [C] Electerm runWidget has a path traversal that leads to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-f77v-9vpc-6pjm
CVE: CVE-2026-43940
CWE: CWE-22, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-f77v-9vpc-6pjm
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.7.16

## Details
### Impact
The `runWidget` function in `src/app/widgets/load-widget.js` constructs a file path by directly concatenating user‑supplied widget identifiers without any sanitisation:

```javascript
const file = `widget-${widgetId}.js`
const widget = require(path.join(__dirname, file))
```

Because `runWidget` is exposed to the renderer process via an asynchronous IPC handler with no input validation, an attacker who achieves JavaScript execution inside the renderer (for example, through a malicious plugin or a cross‑site scripting flaw in the built‑in webview) can abuse a **path traversal** (`../`) to load and execute an arbitrary JavaScript file anywhere on the victim’s filesystem. This gives the attacker local code execution with the full privileges of the electerm process, leading to complete system compromise.

### Patches

Fixed in version >= 3.7.16

### Workarounds
Until a patch is released:
- Do not install or run untrusted plugins.
- Avoid loading arbitrary web content inside electerm’s embedded webview (for example, disable any features that fetch and display remote HTML).
- Run electerm in a sandboxed environment (e.g., with `bubblewrap` on Linux, AppArmor/SELinux profiles, or Windows sandboxed app execution) to limit the impact of any code execution.

### Resources
- [electerm GitHub Repository](https://github.com/electerm/electerm)
- [electerm Security Policy](https://github.com/electerm/electerm/security)
- Vulnerability details originally reported by external researcher (PoC confirmed on v3.7.9, Win10).

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-f77v-9vpc-6pjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43940
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/releases/tag/v3.7.16
