# [C] EverShop Vulnerable to Arbitrary Customer Account Takeover via Exposure of Password Reset Token in API Response

## Summary
Severity: Critical
Advisory: CVE-2026-28213
Aliases: GHSA-cg73-g723-39jw
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28213
Type: osv

## Details
EverShop is a TypeScript-first eCommerce platform. Versions prior to 2.1.1 have a vulnerability in the "Forgot Password" functionality. When specifying a target email address, the API response returns the password reset token. This allows an attacker to take over the associated account. Version 2.1.1 fixes the issue.

## References
- https://github.com/evershopcommerce/evershop/releases/tag/v2.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28213.json
- https://github.com/evershopcommerce/evershop/security/advisories/GHSA-cg73-g723-39jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-28213
