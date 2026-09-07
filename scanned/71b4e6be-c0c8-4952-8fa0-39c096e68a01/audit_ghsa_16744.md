# [M] TYPO3 vulnerable to Cross-Site Scripting in the Form Manager Module

## Summary
Severity: Medium
Advisory: GHSA-v6mw-h7w6-59w3
CVE: CVE-2024-34356
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-v6mw-h7w6-59w3
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.48
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.45
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.37
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.15
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.1.1

## Details
### Problem
The form manager backend module is vulnerable to cross-site scripting. Exploiting this vulnerability requires a valid backend user account with access to the form module.

### Solution
Update to TYPO3 versions 9.5.48 ELTS, 10.4.45 ELTS, 11.5.37 LTS, 12.4.15 LTS, 13.1.1 that fix the problem described.

### Credits
Thanks to TYPO3 core & security team member Benjamin Franzke who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2024-008](https://typo3.org/security/advisory/typo3-core-sa-2024-008)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-v6mw-h7w6-59w3
- https://nvd.nist.gov/vuln/detail/CVE-2024-34356
- https://github.com/TYPO3/typo3/commit/2832e2f51f929aeddb5de7d667538a33ceda8156
- https://github.com/TYPO3/typo3/commit/d0393a879a32fb4e3569acad6bdb5cda776be1e5
- https://github.com/TYPO3/typo3/commit/e95a1224719efafb9cab2d85964f240fd0356e64
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-008
