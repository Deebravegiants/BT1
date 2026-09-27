# [H] Snipe-IT allows users to promote or demote themselves or other users

## Summary
Severity: High
Advisory: GHSA-544r-fc65-v832
CVE: CVE-2024-5685
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-14
Source: https://github.com/advisories/GHSA-544r-fc65-v832
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <6.4.2

## Details
Users with "User:edit" and "Self:api" permissions can promote or demote themselves or other users by performing changes to the group's memberships via API call.This issue affects snipe-it: from v4.6.17 through v6.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5685
- https://github.com/snipe/snipe-it/pull/14745
- https://github.com/snipe/snipe-it/commit/34f1ea1c0ecd403047cd1327569ee391a7201cc1
- https://advisory.checkmarx.net/?search=CVE-2024-5685
- https://devhub.checkmarx.com/cve-details/CVE-2024-5685
- https://github.com/snipe/snipe-it
- https://github.com/snipe/snipe-it/releases/tag/v6.4.2
