# [M] Tornado has incomplete validation of cookie attributes

## Summary
Severity: Medium
Advisory: GHSA-78cv-mqj4-43f7
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-78cv-mqj4-43f7
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.5

## Details
Values passed to the `domain`, `path`, and `samesite` arguments of `RequestHandler.set_cookie` were not completely validated in versions of Tornado prior to 6.5.5. In particular, semicolons would be allowed, which could be used to inject attacker-controlled values for other cookie attributes.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-78cv-mqj4-43f7
- https://github.com/tornadoweb/tornado/commit/24a2d96ea115f663b223887deb0060f13974c104
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.5
