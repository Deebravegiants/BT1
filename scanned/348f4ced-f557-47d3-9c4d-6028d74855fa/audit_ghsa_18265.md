# [M] TYPO3 backend modules have Broken Access Control

## Summary
Severity: Medium
Advisory: GHSA-2fhw-2j7m-mr4m
CVE: CVE-2025-59017
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-2fhw-2j7m-mr4m
Type: github-advisory

## Affected
- Packagist: `typo3/cms-workspaces` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=13.0.0 <13.4.18
- Packagist: `typo3/cms-recycler` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-recycler` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-recycler` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-recycler` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-recycler` — affected >=13.0.0 <13.4.18
- Packagist: `typo3/cms-dashboard` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-dashboard` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-dashboard` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-dashboard` — affected >=13.0.0 <13.4.18
- Packagist: `typo3/cms-beuser` — affected >=13.0.0 <13.4.18
- Packagist: `typo3/cms-beuser` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-beuser` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-beuser` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-beuser` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-backend` — affected >=13.0.0 <13.4.18

## Details
Missing authorization checks in the Backend Routing of TYPO3 CMS versions 9.0.0‑9.5.54, 10.0.0‑10.4.53, 11.0.0‑11.5.47, 12.0.0‑12.4.36, and 13.0.0‑13.4.17 allow backend users to directly invoke AJAX backend routes without having access to the corresponding backend modules.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59017
- https://github.com/TYPO3-CMS/backend/commit/0aedf33d910bceafc2ed0e715743cc0d30124501
- https://github.com/TYPO3-CMS/beuser/commit/eb9b0c14a514a7aada8a2aa30e57696e286044c7
- https://github.com/TYPO3-CMS/dashboard/commit/582006c6bdf251160001eee6624901baccdcfcd2
- https://github.com/TYPO3-CMS/recycler/commit/43475578eb1d9fa3b765537c96bcdf48582ee53b
- https://github.com/TYPO3-CMS/workspaces/commit/32222508043940f9073c338d4205c730a2e02070
- https://typo3.org/security/advisory/typo3-core-sa-2025-021
