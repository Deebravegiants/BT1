# [M] TYPO3 Backend component Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ffcm-vhcw-p32r
CVE: CVE-2016-4056
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-ffcm-vhcw-p32r
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.19

## Details
Cross-site scripting (XSS) vulnerability in the Backend component in TYPO3 6.2.x before 6.2.19 allows remote attackers to inject arbitrary web script or HTML via the module parameter when creating a bookmark.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4056
- https://github.com/TYPO3/typo3
- https://labs.integrity.pt/advisories/cve-pending-stored-cross-site-scripting-in-typo3-bookmarks
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-006
- http://www.openwall.com/lists/oss-security/2016/04/21/1
