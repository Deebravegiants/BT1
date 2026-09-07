# [M] Pimcore vulnerable to stored stored Cross-site Scripting via`properties` when creating new users

## Summary
Severity: Medium
Advisory: GHSA-4849-x3jx-45qr
CVE: CVE-2022-3211
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-4849-x3jx-45qr
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.6

## Details
Pimcore prior to 10.5.6 is vulnerable to stored cross-site scripting. This occurs when an attacker injects a payload when adding properties for a new user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3211
- https://github.com/pimcore/pimcore/pull/13129
- https://github.com/pimcore/pimcore/commit/0508c491c6a4f3d119ec8dcf444e52ff25028c36
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/31ac0506-ae38-4128-a46d-71d5d079f8b7
