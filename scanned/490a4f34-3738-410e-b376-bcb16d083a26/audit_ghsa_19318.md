# [H] The TYPO3 CMS Backend has Broken Authentication in Backend MFA

## Summary
Severity: High
Advisory: GHSA-744g-7qm9-hjh9
CVE: CVE-2025-47941
CWE: CWE-288
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-20
Source: https://github.com/advisories/GHSA-744g-7qm9-hjh9
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=12.0.0 <12.4.31
- Packagist: `typo3/cms-backend` — affected >=13.0.0 <13.4.12

## Details
### Problem
The multifactor authentication (MFA) dialog presented during backend login can be bypassed due to insufficient enforcement of access restrictions on all backend routes.

Successful exploitation requires valid backend user credentials, as MFA can only be bypassed after successful authentication.

### Solution
Update to TYPO3 versions 12.4.31 LTS, 13.4.12 LTS that fix the problem described.

### Credits
Thanks to Jens Jacobsen and Y. Kahveci for reporting this issue, and to TYPO3 security team member Torben Hansen for fixing it.

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-744g-7qm9-hjh9
- https://nvd.nist.gov/vuln/detail/CVE-2025-47941
- https://github.com/TYPO3-CMS/backend/commit/034f589029952084771c5f98d42ed0f69f9a7ead
- https://github.com/TYPO3-CMS/backend
- https://typo3.org/security/advisory/typo3-core-sa-2025-015
