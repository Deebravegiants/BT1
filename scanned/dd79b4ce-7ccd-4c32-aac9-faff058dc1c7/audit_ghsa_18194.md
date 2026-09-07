# [H] TYPO3 Workspaces Module Information Disclosure

## Summary
Severity: High
Advisory: GHSA-w2pf-7q5w-2cgw
CVE: CVE-2025-59018
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-w2pf-7q5w-2cgw
Type: github-advisory

## Affected
- Packagist: `typo3/cms-workspaces` — affected >=9.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=10.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=11.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=12.0.0 <12.4.37
- Packagist: `typo3/cms-workspaces` — affected >=13.0.0 <13.4.18

## Details
Missing authorization checks in the Workspace Module of TYPO3 CMS versions 9.0.0‑9.5.54, 10.0.0‑10.4.53, 11.0.0‑11.5.47, 12.0.0‑12.4.36, and 13.0.0‑13.4.17 allow backend users to directly invoke the corresponding AJAX backend route to disclose sensitive information without having access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59018
- https://github.com/TYPO3-CMS/workspaces/commit/114c189c7b30181cee96d176e31f212b02d14d4d
- https://github.com/TYPO3-CMS/workspaces
- https://typo3.org/security/advisory/typo3-core-sa-2025-022
