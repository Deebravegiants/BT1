# [M] TYPO3 Bookmark Toolbar vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-xrcq-533q-8rxw
CVE: CVE-2025-59014
CWE: CWE-248
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-xrcq-533q-8rxw
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=13.0.0 <13.4.18

## Details
An uncaught exception in the Bookmark Toolbar of TYPO3 CMS versions 11.0.0–11.5.47, 12.0.0–12.4.36, and 13.0.0–13.4.17 lets administrator‑level backend users trigger a denial‑of‑service condition in the backend user interface by saving manipulated data in the bookmark toolbar.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59014
- https://github.com/TYPO3-CMS/backend/commit/04db7e25de1d3bb2d082ba68f7f974ccd917cc3f
- https://github.com/TYPO3-CMS/backend
- https://typo3.org/security/advisory/typo3-core-sa-2025-018
