# [M] TYPO3 cross-site scripting (XSS) vulnerability in the RemoveXSS function and the backend

## Summary
Severity: Medium
Advisory: GHSA-mwqv-jff6-5v62
CVE: CVE-2010-3715
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mwqv-jff6-5v62
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=4.2.0 <4.2.15
- Packagist: `typo3/cms-backend` — affected >=4.3.0 <4.3.7
- Packagist: `typo3/cms-backend` — affected >=4.4.0 <4.4.4

## Details
Multiple cross-site scripting (XSS) vulnerabilities in TYPO3 4.2.x before 4.2.15, 4.3.x before 4.3.7, and 4.4.x before 4.4.4 allow remote attackers to inject arbitrary web script or HTML via vectors related to (1) the RemoveXSS function, and allow remote authenticated users to inject arbitrary web script or HTML via vectors related to (2) the backend.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3715
- https://github.com/TYPO3/typo3/commit/38ec239a35d50746a2f95eef004227acd1932b81
- https://github.com/TYPO3/typo3/commit/aba23d6f12775d31acd9b7197d5eeddca09d3574
- https://github.com/TYPO3/typo3/commit/ce47d8dcdc2cd67b7866a3a53d36aa8203311780
- https://github.com/TYPO3-CMS/backend
- https://web.archive.org/web/20111220151231/http://www.securityfocus.com/bid/43786
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2010-020
- http://www.debian.org/security/2010/dsa-2121
