# [M] copyparty: Sharing a single file does not fully restrict access to other files in source folder

## Summary
Severity: Medium
Advisory: GHSA-pxvw-4w88-6x95
CVE: CVE-2025-58753
CWE: CWE-552, CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-pxvw-4w88-6x95
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.19.8

## Details
There was a missing permission-check in the shares feature (the `shr` global-option).

When a share is created for just one file inside a folder, it was possible to access the other files inside that folder by guessing the filenames.

It was not possible to descend into subdirectories in this manner; only the sibling files were accessible.

This issue did not affect filekeys or dirkeys.

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-pxvw-4w88-6x95
- https://nvd.nist.gov/vuln/detail/CVE-2025-58753
- https://github.com/9001/copyparty/commit/e0a92ba72d46074209a9c304eb2a01ca0429e60c
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.19.8
