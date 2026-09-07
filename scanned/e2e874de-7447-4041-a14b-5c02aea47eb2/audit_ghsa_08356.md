# [M] Weblate vulnerable to XSS via crafted Markdown

## Summary
Severity: Medium
Advisory: GHSA-5cmv-3rc4-7279
CVE: CVE-2026-44264
CWE: CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-5cmv-3rc4-7279
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17.1

## Details
### Impact
The Markdown renderer used in user comments and other user-provided content didn't properly sanitize some attributes.

### Patches
* https://github.com/WeblateOrg/weblate/pull/19259

### Workarounds
Even though the attacker might be able to inject code into the HTML, the Weblate's strict CSP should mitigate the risks.

### Acknowlegement
Michal Čihař has identified and fixed this vulnerability.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-5cmv-3rc4-7279
- https://nvd.nist.gov/vuln/detail/CVE-2026-44264
- https://github.com/WeblateOrg/weblate/pull/19259
- https://github.com/WeblateOrg/weblate/commit/85abc9df88b7464f4c0e794aef752e45f4230f75
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.17.1
