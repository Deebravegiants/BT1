# [M] TYPO3 Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-87hc-phmj-rhgh
CVE: CVE-2017-6370
CWE: CWE-319
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-87hc-phmj-rhgh
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected 7.6.15

## Details
TYPO3 7.6.15 sends an http request to an index.php?loginProvider URI in cases with an https Referer, which allows remote attackers to obtain sensitive cleartext information by sniffing the network and reading the userident and username fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6370
- https://github.com/TYPO3/typo3
- https://github.com/faizzaidi/TYPO3-v7.6.15-Unencrypted-Login-Request
- http://www.securityfocus.com/bid/97071
