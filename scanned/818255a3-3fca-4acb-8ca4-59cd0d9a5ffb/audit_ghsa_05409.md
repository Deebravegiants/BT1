# [M] TYPO3 CMS Allows Broken Access Control in Edit Document Controller

## Summary
Severity: Medium
Advisory: GHSA-5j7q-wmh7-cqhg
CVE: CVE-2025-59020
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-5j7q-wmh7-cqhg
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=14.0.0 <14.0.2
- Packagist: `typo3/cms-backend` — affected >=13.0.0 <13.4.23
- Packagist: `typo3/cms-backend` — affected >=12.0.0 <12.4.41
- Packagist: `typo3/cms-backend` — affected >=11.0.0 <11.5.49
- Packagist: `typo3/cms-backend` — affected >=10.0.0 <10.4.55

## Details
### Problem
By exploiting the `defVals` parameter, attackers could bypass field‑level access checks during record creation in the TYPO3 backend. This gave them the ability to insert arbitrary data into prohibited exclude fields of a database table for which the user already has write permission for a reduced set of fields.

### Solution
Update to TYPO3 versions 10.4.55 ELTS, 11.5.49 ELTS, 12.4.41 LTS, 13.4.23 LTS, 14.0.2 that fix the problem described.

### Credits
Thanks to Daniel Windloff for reporting this issue, and to TYPO3 core & security team member Benjamin Franzke for fixing it.

### References
* [TYPO3-CORE-SA-2026-001](https://typo3.org/security/advisory/typo3-core-sa-2026-001)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-5j7q-wmh7-cqhg
- https://nvd.nist.gov/vuln/detail/CVE-2025-59020
- https://github.com/TYPO3/typo3/commit/ac3f792bd5ab7c58153fc1075cb9e001c9cebe3b
- https://github.com/TYPO3/typo3/commit/cd11a19958d823d12d028f9345b41739c7e70118
- https://github.com/TYPO3/typo3/commit/fb98378a8fd30dd50d89a3d1a420780819f38232
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-001
