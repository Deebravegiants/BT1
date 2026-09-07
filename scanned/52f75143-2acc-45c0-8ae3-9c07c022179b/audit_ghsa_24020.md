# [M] Typo3 Cross-Site Scripting in Flash component (ELTS)

## Summary
Severity: Medium
Advisory: GHSA-qvhv-pwww-53jj
CVE: CVE-2020-8091
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qvhv-pwww-53jj
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.2.0
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.39

## Details
TYPO3 6.2.0 to 6.2.38 ELTS and 7.0.0 to 7.1.0 included a vulnerable external component, which could allow an unauthenticated, remote attacker to conduct a cross-site scripting (XSS) attack on a targeted system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8091
- https://github.com/TYPO3/typo3/commit/482e2e992f80f5e38cb48fcaea40fd9812a5252c
- https://github.com/TYPO3/typo3
- https://github.com/TYPO3/typo3/blob/4cb53e828bd5138d180cdf9cac1ccf7fd31086d2/typo3/sysext/core/Documentation/Changelog/7.2/Breaking-65962-WebSVGLibraryAndAPIRemoved.rst
- https://typo3.org/security/advisory/typo3-psa-2019-003
- https://www.purplemet.com/blog/typo3-xss-vulnerability
