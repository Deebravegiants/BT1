# [M] TYPO3 CMS uses insufficient entropy when generating passwords

## Summary
Severity: Medium
Advisory: GHSA-p5jq-5383-qvc7
CVE: CVE-2025-59015
CWE: CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-p5jq-5383-qvc7
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.18

## Details
A deterministic three‑character prefix in the Password Generation component of TYPO3 CMS versions 12.0.0–12.4.36 and 13.0.0–13.4.17 reduces entropy, allowing attackers to carry out brute‑force attacks more quickly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59015
- https://github.com/TYPO3-CMS/core/commit/d2057cc7b2c2db417a2af38c30cb9da42302ab70
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2025-019
