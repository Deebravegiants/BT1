# [H] EverShop vulnerable to improper authorization in GraphQL endpoints

## Summary
Severity: High
Advisory: GHSA-ggpm-9qfx-mhwg
CVE: CVE-2023-46942
CWE: CWE-285, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-13
Source: https://github.com/advisories/GHSA-ggpm-9qfx-mhwg
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.9

## Details
Lack of authentication in NPM's package @evershop/evershop before version 1.0.0-rc.9, allows remote attackers to obtain sensitive information via improper authorization in GraphQL endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46942
- https://github.com/evershopcommerce/evershop/commit/6e16f046e0b95efa16431a5ea41c22215273e9dd
- https://advisory.checkmarx.net/advisory/CVE-2023-46942
- https://devhub.checkmarx.com/cve-details/CVE-2023-46942
- https://devhub.checkmarx.com/cve-details/Cx00cea2d5-d2c5
- https://github.com/evershopcommerce/evershop
