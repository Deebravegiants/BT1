# [M] YetiForceCRM Directory Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-394m-vxwj-363j
CVE: CVE-2023-49508
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-16
Source: https://github.com/advisories/GHSA-394m-vxwj-363j
Type: github-advisory

## Affected
- Packagist: `yetiforce/yetiforce-crm` — affected >=0 <6.5.0

## Details
Directory Traversal vulnerability in YetiForceCompany YetiForceCRM versions 6.4.0 and before allows a remote authenticated attacker to obtain sensitive information via the license parameter in the LibraryLicense.php component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49508
- https://github.com/YetiForceCompany/YetiForceCRM/commit/ba3a348aa6ecdf0a1d8b289cbb679bebcda7a132
- https://github.com/YetiForceCompany/YetiForceCRM
- https://github.com/c4v4r0n/Research/tree/main/CVE-2023-49508
- https://huntr.com/bounties/29ed641d-eb03-4532-aed4-f96e11f78983
