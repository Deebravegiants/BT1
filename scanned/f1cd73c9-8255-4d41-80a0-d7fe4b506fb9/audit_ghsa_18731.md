# [M] Anubis vulnerable to possible XSS via redir parameter when using subrequest auth mode

## Summary
Severity: Medium
Advisory: GHSA-cf57-c578-7jvv
CVE: CVE-2025-64716
CWE: CWE-601, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-cf57-c578-7jvv
Type: github-advisory

## Affected
- Go: `github.com/TecharoHQ/anubis` — affected >=0 <1.23.0

## Details
### Summary

When using subrequest authentication, Anubis did not perform validation of the redirect URL and redirects user to any URL scheme. While most modern browsers do not allow a redirect to `javascript:` URLs, it could still trigger dangerous behavior in some cases.

`GET https://example.com/.within.website/?redir=javascript:alert()` responds with `Location: javascript:alert()`.

### Impact

Anybody with a subrequest authentication seems affected. Using `javascript:` URLs will probably be blocked by most modern browsers, but using custom protocols for third-party applications might still trigger dangerous operations.

### Note

This was originally reported by @mbiesiad against Weblate.

## References
- https://github.com/TecharoHQ/anubis/security/advisories/GHSA-cf57-c578-7jvv
- https://nvd.nist.gov/vuln/detail/CVE-2025-64716
- https://github.com/TecharoHQ/anubis/commit/7ed1753fcced351c81961bf520a7bfb2caac6e88
- https://github.com/TecharoHQ/anubis
- https://pkg.go.dev/vuln/GO-2025-4086
