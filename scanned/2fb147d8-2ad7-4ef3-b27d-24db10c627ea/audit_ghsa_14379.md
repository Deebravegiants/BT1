# [H] Company admin role gives excessive privileges in eZ Platform Ibexa

## Summary
Severity: High
Advisory: GHSA-qq2j-9pf8-g58c
CVE: CVE-2022-48365
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-12
Source: https://github.com/advisories/GHSA-qq2j-9pf8-g58c
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.5.0 <7.5.30
- Packagist: `ezsystems/ezplatform-kernel` — affected >=1.3.0 <1.3.26

## Details
Users with the Company admin role (introduced by the company account feature in v4) can assign any role to any user. This also applies to any other user that has the role / assign policy. Any subtree limitation in place does not have any effect.

The role / assign policy is typically only given to administrators, which limits the scope in most cases, but please verify who has this policy in your installaton. The fix ensures that subtree limitations are working as intended.

## References
- https://github.com/ezsystems/ezplatform-kernel/security/advisories/GHSA-8h83-chh2-fchp
- https://github.com/ezsystems/ezpublish-kernel/security/advisories/GHSA-99r3-xmmq-7q7g
- https://nvd.nist.gov/vuln/detail/CVE-2022-48365
- https://github.com/ezsystems/ezpublish-kernel/commit/957e67a08af2b3265753f9763943e8225ed779ab
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-009-critical-vulnerabilities-in-graphql-role-assignment-ct-editing-and-drafts-tooltips
- https://github.com/ezsystems/ezpublish-kernel
