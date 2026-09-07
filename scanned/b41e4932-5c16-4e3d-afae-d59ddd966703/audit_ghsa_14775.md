# [M] TYPO3 Cross-Site Scripting in Online Media Asset Rendering

## Summary
Severity: Medium
Advisory: GHSA-8m6j-p5jv-v69w
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-8m6j-p5jv-v69w
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.32
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.21
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.2

## Details
Failing to properly encode user input, online media asset rendering (`*.youtube` and `*.vimeo` files) is vulnerable to cross-site scripting. A valid backend user account or write access on the server system (e.g. SFTP) is needed in order to exploit this vulnerability.

## References
- https://github.com/TYPO3/typo3/commit/20927adfb8aae0093508c904937e40114b92a90c
- https://github.com/TYPO3/typo3/commit/a32a9a746f807b14571139f0cb7caa00b8d037a5
- https://github.com/TYPO3/typo3/commit/c9174937802581bfecfaa788512a4f6e5cf8e9c7
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-12-11-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-006
