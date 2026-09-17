# [H] @hapi/content header parser has a parameter smuggling issue that allows upload-filter bypass via duplicate parameters

## Summary
Severity: High
Advisory: GHSA-36hh-x5p5-jgc8
CVE: CVE-2026-44974
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-36hh-x5p5-jgc8
Type: github-advisory

## Affected
- npm: `@hapi/content` — affected >=0 <6.0.2

## Details
### Impact
The two parsers resolved duplicates inconsistently and silently:
- `Content.disposition()` retained the last occurrence of each parameter.
- `Content.type()` retained the first occurrence of charset and boundary.

Either behavior creates a parameter-smuggling primitive when another component in the request-processing chain (a WAF, reverse proxy, security filter, or alternate parser) resolves duplicates the opposite way. The primary attack vector is upload filename allowlist bypass:

`Content-Disposition: form-data; name="file"; filename="safe.txt"; filename="shell.php"`

### Patches
The issue has been patched in 6.0.2.

### Workarounds
Pre or post validate headers looking for duplicates.

### Resources
- [RFC 6266 §4.1 — Content-Disposition syntax](https://www.rfc-editor.org/rfc/rfc6266#section-4.1)
- [RFC 7231 §3.1.1.1 — Content-Type syntax](https://www.rfc-editor.org/rfc/rfc7231#section-3.1.1.1)
- [RFC 7230 §3.2.6 — token character set](https://www.rfc-editor.org/rfc/rfc7230#section-3.2.6)

## References
- https://github.com/hapijs/content/security/advisories/GHSA-36hh-x5p5-jgc8
- https://github.com/hapijs/content/commit/3850079550c191d25e3643dc82a6d61144db8c2f
- https://github.com/hapijs/content
