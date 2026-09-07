# [M] Open redirect in caddy

## Summary
Severity: Medium
Advisory: GHSA-2927-hv3p-f3vp
CVE: CVE-2022-29718
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-2927-hv3p-f3vp
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy` — affected >=0 <2.5.0
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.5.0

## Details
Caddy v2.4 was discovered to contain an open redirect vulnerability. A remote unauthenticated attacker may exploit this vulnerability to redirect users to arbitrary web URLs by tricking the victim users to click on crafted links.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29718
- https://github.com/caddyserver/caddy/pull/4499
- https://github.com/caddyserver/caddy/pull/4499/commits/b23bdcf99cfbd09d50555a999a16468404789230
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v2.5.0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CP2VIUT5IKA3OKM6YWA5LTLJ2GTEIH7C
