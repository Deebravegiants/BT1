# [H] Integer Overflow or Wraparound in Microweber

## Summary
Severity: High
Advisory: GHSA-3qr6-qrqm-8v86
CVE: CVE-2022-1036
CWE: CWE-190
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-23
Source: https://github.com/advisories/GHSA-3qr6-qrqm-8v86
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.12

## Details
In Microweber prior to 1.2.12, a user can create an account with a password thousands of characters in length, leading to memory corruption/integer overflow. Version 1.2.2 sets maximum password length at 500 characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1036
- https://github.com/microweber/microweber/commit/82be4f0b4729be870ccefdae99a04833f134aa6a
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/db615581-d5a9-4ca5-a3e9-7a39eceaa424
