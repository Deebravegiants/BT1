# [M] Flask-AppBuilder's login form allows browser to cache sensitive fields 

## Summary
Severity: Medium
Advisory: GHSA-fw5r-6m3x-rh7p
CVE: CVE-2024-45314
CWE: CWE-525
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-04
Source: https://github.com/advisories/GHSA-fw5r-6m3x-rh7p
Type: github-advisory

## Affected
- PyPI: `flask-appbuilder` — affected >=0 <4.5.1

## Details
### Impact
Auth DB login form default cache directives allows browser to locally store sensitive data. This can be an issue on environments using shared computer resources.

### Patches
Upgrade flask-appbuilder to version 4.5.1

### Workarounds
If upgrading is not possible configure your web server to send the following HTTP headers for /login:
"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
"Pragma": "no-cache"
"Expires": "0"

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-fw5r-6m3x-rh7p
- https://nvd.nist.gov/vuln/detail/CVE-2024-45314
- https://github.com/dpgaspar/Flask-AppBuilder/commit/3030e881d2e44f4021764e18e489fe940a9b3636
- https://github.com/dpgaspar/Flask-AppBuilder
