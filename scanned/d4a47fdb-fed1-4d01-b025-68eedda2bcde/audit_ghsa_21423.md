# [C] Ibexa DXP users with the Company admin role can assign any role to any user

## Summary
Severity: Critical
Advisory: GHSA-394j-x37r-2q27
Ecosystem: Packagist
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-394j-x37r-2q27
Type: github-advisory

## Affected
- Packagist: `ibexa/core` — affected >=4.2.0 <4.2.3

## Details
Critical severity. Users with the Company admin role (introduced by the company account feature in v4) can assign any role to any user. This also applies to any other user that has the role / assign policy. Any subtree limitation in place does not have any effect.

The role / assign policy is typically only given to administrators, which limits the scope in most cases, but please verify who has this policy in your installaton. The fix ensures that subtree limitations are working as intended.

## References
- https://github.com/ibexa/core/security/advisories/GHSA-394j-x37r-2q27
- https://github.com/ibexa/core/commit/da3642c98d2c94607bb53ed2e42654eb92b42e17
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-009-critical-vulnerabilities-in-graphql-role-assignment-ct-editing-and-drafts-tooltips
- https://github.com/ibexa/core
