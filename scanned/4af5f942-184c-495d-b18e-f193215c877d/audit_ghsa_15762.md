# [H] aimeos/ai-admin-graphql improper access control vulnerability allows an editor to modify admin account

## Summary
Severity: High
Advisory: GHSA-vc7j-99jw-jrqm
CVE: CVE-2024-39323
CWE: CWE-1220, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2024-07-02
Source: https://github.com/advisories/GHSA-vc7j-99jw-jrqm
Type: github-advisory

## Affected
- Packagist: `aimeos/ai-admin-graphql` — affected >=2022.04.1 <2022.10.10
- Packagist: `aimeos/ai-admin-graphql` — affected >=2023.04.1 <2023.10.6
- Packagist: `aimeos/ai-admin-graphql` — affected >=2024.04.1 <2024.04.6

## Details
aimeos/ai-admin-graphql is the Aimeos GraphQL API admin interface. Starting in version 2022.04.01 and prior to versions 2022.10.10, 2023.10.6, and 2024.04.6, an improper access control vulnerability allows an editor to modify and take over an admin account in the back end. Versions 2022.10.10, 2023.10.6, and 2024.04.6 fix this issue.

## References
- https://github.com/aimeos/ai-admin-graphql/security/advisories/GHSA-vc7j-99jw-jrqm
- https://nvd.nist.gov/vuln/detail/CVE-2024-39323
- https://github.com/aimeos/ai-admin-graphql/commit/2d89d98cdcad880a9244b50736b08c1a171379ca
- https://github.com/aimeos/ai-admin-graphql/commit/54d6b7cf4530cb3b95f52775c24056c48e6d26e9
- https://github.com/aimeos/ai-admin-graphql/commit/787028de0a3ecbf3e9f63ab1454eac99ce7693a9
- https://github.com/aimeos/ai-admin-graphql
