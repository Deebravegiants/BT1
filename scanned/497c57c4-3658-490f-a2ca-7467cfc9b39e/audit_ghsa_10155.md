# [H] Tornado has cookie attribute injection via .RequestHandler.set_cookie

## Summary
Severity: High
Advisory: GHSA-fqwm-6jpj-5wxc
CVE: CVE-2026-35536
CWE: CWE-159
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-fqwm-6jpj-5wxc
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.5

## Details
In Tornado before 6.5.5, cookie attribute injection could occur because the domain, path, and samesite arguments to `.RequestHandler.set_cookie` were not checked for crafted characters.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-78cv-mqj4-43f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35536
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.5
