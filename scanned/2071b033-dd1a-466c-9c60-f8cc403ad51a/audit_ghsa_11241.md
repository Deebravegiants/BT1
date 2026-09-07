# [H] FileBrowser Quantum: Stored XSS in public share page via unsanitized share metadata (text/template misuse)

## Summary
Severity: High
Advisory: GHSA-r633-fcgp-m532
CVE: CVE-2026-30934
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-r633-fcgp-m532
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser` — affected >=0 <0.0.0-20260307130210-09713b32a5f6

## Details
## Summary
Stored XSS is possible via share metadata fields (e.g., `title`, `description`) that are rendered into HTML for `/public/share/<hash>` without context-aware escaping. The server uses `text/template` instead of `html/template`, allowing injected scripts to execute when victims visit the share URL.

## Details
The server renders `public/index.html` using `text/template` and injects user-controlled share fields (title/description/etc.) into HTML contexts. `text/template` does not perform HTML contextual escaping like `html/template`. Because share metadata is persistent, the payload becomes stored and executes whenever a victim opens the affected share page.

Relevant code paths:
- `backend/http/static.go` (template rendering and share metadata assignment)
- `backend/http/httpRouter.go` (template initialization)
- `frontend/public/index.html` (insertion points for title/description and related fields)

## PoC
1. Login as a user with share creation permission.
2. Create a share (`POST /api/share`) with malicious metadata:
   - `title = </title><script>alert("xss")</script><title>`
3. Open the resulting `/public/share/<hash>` URL in a browser.
4. **Expected:** Payload is safely escaped and displayed as text.
5. **Actual:** JavaScript executes in victim's browser (stored XSS).

Tested on Docker image: `gtstef/filebrowser:stable` (version `v1.2.1-stable`).

## Impact
- Arbitrary script execution in application origin.
- Potential account/session compromise, CSRF-like action execution, data exfiltration from authenticated contexts.
- Affects anyone (including unauthenticated visitors) opening the malicious share URL.
- The XSS is stored and persistent — no social engineering beyond sharing the link is required.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-r633-fcgp-m532
- https://nvd.nist.gov/vuln/detail/CVE-2026-30934
- https://github.com/gtsteffaniak/filebrowser
- https://github.com/gtsteffaniak/filebrowser/releases/tag/v1.2.2-stable
- https://github.com/gtsteffaniak/filebrowser/releases/tag/v1.3.1-beta
- https://pkg.go.dev/vuln/GO-2026-4660
