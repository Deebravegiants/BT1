# [M] Flask-AppBuilder's OAuth login page subject to Cross Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-fqxj-46wg-9v84
CVE: CVE-2024-27083
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-28
Source: https://github.com/advisories/GHSA-fqxj-46wg-9v84
Type: github-advisory

## Affected
- PyPI: `Flask-AppBuilder` — affected >=4.1.4 <4.2.1

## Details
### Impact
A Cross-Site Scripting (XSS) vulnerability has been discovered on the OAuth login page. An attacker could trick a user to follow a specially crafted URL to the OAuth login page. This URL could inject and execute malicious javascript code that would get executed on the user's browser.

Impacted versions:
Flask-AppBuilder version 4.1.4 up to and including 4.2.0

### Patches
This issue was introduced on 4.1.4 and patched on 4.2.1, user's should upgrade to 4.2.1 or newer versions.

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-fqxj-46wg-9v84
- https://nvd.nist.gov/vuln/detail/CVE-2024-27083
- https://github.com/dpgaspar/Flask-AppBuilder/commit/3d17741886e4b3c384d0570de69689e4117aa812
- https://github.com/dpgaspar/Flask-AppBuilder
