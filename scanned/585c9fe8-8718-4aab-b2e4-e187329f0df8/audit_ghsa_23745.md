# [H] url_redirect for Typo3 SQLi Vulnerability

## Summary
Severity: High
Advisory: GHSA-hcpv-xh8q-f3vq
CVE: CVE-2019-16682
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hcpv-xh8q-f3vq
Type: github-advisory

## Affected
- Packagist: `sfroemken/url_redirect` — affected >=0 <1.2.2

## Details
The url_redirect (aka URL redirect) extension through 1.2.1 for TYPO3 fails to properly sanitize user input and is susceptible to SQL Injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16682
- https://github.com/froemken/url_redirect/commit/91cc8da2cf122eff0ecca14e9919ece7fca0a053
- https://extensions.typo3.org/extension/url_redirect
- https://github.com/froemken/url_redirect
- https://typo3.org/security/advisory/typo3-ext-sa-2019-015
