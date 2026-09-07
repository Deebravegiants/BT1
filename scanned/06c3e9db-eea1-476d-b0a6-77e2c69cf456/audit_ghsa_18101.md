# [M] TYPO3 CSV download feature information disclosure

## Summary
Severity: Medium
Advisory: GHSA-j8vm-7q52-2m2m
CVE: CVE-2025-59019
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-j8vm-7q52-2m2m
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=13.0.0 <13.4.18
- Packagist: `typo3/cms-recordlist` — affected >=11.0.0 <12.4.37

## Details
Missing authorization checks in the CSV download feature of TYPO3 CMS versions 11.0.0‑11.5.47, 12.0.0‑12.4.36, and 13.0.0‑13.4.17 allow backend users to disclose information from arbitrary database tables stored within the users' web mounts without having access to them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59019
- https://github.com/TYPO3-CMS/backend/commit/c983415f062c32f8edbb78544a0ff3219bc35d17
- https://typo3.org/security/advisory/typo3-core-sa-2025-023
