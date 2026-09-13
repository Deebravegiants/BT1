# [C] EverShop at risk to unauthorized access via weak HMAC secret

## Summary
Severity: Critical
Advisory: GHSA-32r3-57hp-cgfw
CVE: CVE-2023-46943
CWE: CWE-284, CWE-798
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-13
Source: https://github.com/advisories/GHSA-32r3-57hp-cgfw
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.9

## Details
An issue was discovered in NPM's package @evershop/evershop before version 1.0.0-rc.9. The HMAC secret used for generating tokens is hardcoded as "secret". A weak HMAC secret poses a risk because attackers can use the predictable secret to create valid JSON Web Tokens (JWTs), allowing them access to important information and actions within the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46943
- https://github.com/evershopcommerce/evershop/commit/96d9ca3e024e0b63c538911e4a914df3d287cc9f
- https://advisory.checkmarx.net/advisory/CVE-2023-46943
- https://devhub.checkmarx.com/cve-details/CVE-2023-46943
- https://github.com/evershopcommerce/evershop
