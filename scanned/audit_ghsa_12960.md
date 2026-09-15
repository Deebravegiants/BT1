# [M] Admidio Insufficient Session Expiration vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qq8m-9rpx-w2fm
CVE: CVE-2023-4190
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-06
Source: https://github.com/advisories/GHSA-qq8m-9rpx-w2fm
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <4.2.11

## Details
Insufficient Session Expiration in GitHub repository admidio/admidio prior to 4.2.11. This vulnerability allows a user's session to remain valid even after the user has logged out, potentially granting unauthorized access to sensitive areas and functionalities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4190
- https://github.com/admidio/admidio/commit/391fb2af5bee641837a58e7dd66ff76eac92bb74
- https://github.com/admidio/admidio
- https://huntr.dev/bounties/71bc75d2-320c-4332-ad11-9de535a06d92
