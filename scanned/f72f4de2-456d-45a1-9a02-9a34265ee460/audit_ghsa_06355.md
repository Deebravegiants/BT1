# [H] Open WebUI: Same-origin XSS to account takeover via terminal file-preview iframe hardcoding allow-same-origin

## Summary
Severity: High
Advisory: GHSA-3xpf-xq7r-v8c5
CVE: CVE-2026-70486
CWE: CWE-1021, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-3xpf-xq7r-v8c5
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.0 <0.11.0

## Details
## Summary
Any authenticated user with access to a terminal server could get script of their choosing to run in the Open WebUI origin itself. The HTML file preview rendered terminal-served files in an iframe whose sandbox always granted `allow-same-origin` alongside `allow-scripts`, and the file is served from a path on the application's own origin, so the sandbox provided no isolation at all. Script in a previewed file could read the victim's session token and take over the account.

## Preconditions
- At least one terminal server configured by an admin (`TERMINAL_SERVER_CONNECTIONS`, empty by default) and reachable by the victim. Deployments with no terminal server configured are not affected.
- The attacker needs a normal authenticated account with access to that terminal server, no admin rights.
- No victim interaction beyond having the chat open: a `display_file` tool call opens the preview automatically.
- `TERMINAL_PROXY_HEADERS` unset, which is the default. An operator who had already set a restrictive Content-Security-Policy through it was not exposed, since those headers are merged into every proxied response including the served file.
- The `iframeSandboxAllowSameOrigin` user setting is off by default, but the affected branch ignored it entirely.

## Impact
The previewed document runs in the application origin, so it can reach the parent window, read the session token out of `localStorage` and exfiltrate it, which is full account takeover of the victim. If the victim is an admin, or any user holding `workspace.functions`, that takeover extends to server-side code execution through Functions. Getting the malicious file written and displayed still requires a prompt-injection or a social step, which is what keeps the complexity high rather than trivial. Instances with no terminal server configured were never affected, and neither was the `srcdoc` preview path.

## Fix
Fixed in 0.11.0 by 65a5fad7b (#26907). The `serveUrl` preview branch now gates `allow-same-origin` behind the same `iframeSandboxAllowSameOrigin` setting the `srcdoc` branch already used, so by default the preview loads at an opaque origin and cannot reach the parent context. Upgrading is sufficient, no configuration change is required, and HTML previews continue to render normally.

## Root cause
- `src/lib/components/chat/FileNav/FilePreview.svelte`, the `serveUrl` iframe branch, reached for HTML files served through `/api/v1/terminals/{id}/files/serve/...`.
- Present from 0.9.0, where that branch was introduced, through 0.10.2.

The component grew two preview paths. The `srcdoc` path was hardened: same-origin became opt-in and a CSP was injected into the document. The `serveUrl` path, added later for files streamed from a terminal server, kept a static sandbox string with `allow-same-origin` baked into it. Because the terminal proxy is mounted under the application's own origin and forwards the upstream response without adding a Content-Security-Policy of its own unless the operator configured one, and no global CSP is set, the sandbox was the only isolation boundary left, and it was granting precisely the permission that dissolved it.

## Proof of concept
Write an HTML file containing a script that reads `window.parent.localStorage.token` to a terminal server the victim can reach, then trigger `display_file` for that file. The chat handler opens the preview on the resulting `terminal:display_file` event with no click, the script executes at the application origin, and the token is exfiltrated.

## Credits
Reported by @manus-use (researcher zx / Jace).

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3xpf-xq7r-v8c5
- https://github.com/open-webui/open-webui/pull/26907
- https://github.com/open-webui/open-webui/commit/65a5fad7b97db99d490d81f4e0860282c3a4543c
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
