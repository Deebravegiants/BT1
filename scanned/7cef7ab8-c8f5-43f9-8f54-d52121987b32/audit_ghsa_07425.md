# [H] openhole-server vulnerable to path traversal via URL-decoded request path

## Summary
Severity: High
Advisory: GHSA-fh2f-xfxc-q9cc
CVE: CVE-2026-54650
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-fh2f-xfxc-q9cc
Type: github-advisory

## Affected
- Go: `github.com/bablilayoub/openhole` — affected >=0 <0.1.2

## Details
## Summary

openhole-server forwarded the URL-decoded request path (`r.URL.Path`) to tunnel clients instead of the original request-target. Percent-encoded dot-segments (`%2e`) and separators (`%2f`) were decoded to `../` and `/` before reaching the local service.

Go's ServeMux rejects literal `../` paths, but percent-encoded traversal sequences bypassed this and were delivered to backends as working path traversal.

## Impact

An unauthenticated remote attacker could read files outside the published web root on tunneled local services that resolve paths without canonicalization.

Example:
- `/%2e%2e/secret.txt` → file outside web root
- `/%2e%2e/%2e%2e/etc/passwd` → sensitive files

Encoded slashes (`/a%2fb`) could also bypass path-based access controls.

## Fix

v0.1.2 forwards `r.URL.EscapedPath()` on the server and preserves the request-target on the CLI client.

Users should upgrade both openhole-server and the openhole CLI to v0.1.2 or later.

## References
- https://github.com/bablilayoub/openhole/security/advisories/GHSA-fh2f-xfxc-q9cc
- https://github.com/bablilayoub/openhole/commit/a28c27adde2a7ed0c347b730c8707208c0f78ed3
- https://github.com/bablilayoub/openhole
- https://github.com/bablilayoub/openhole/releases/tag/v0.1.2
