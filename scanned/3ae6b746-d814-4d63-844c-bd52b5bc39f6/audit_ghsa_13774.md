# [M] OroCommerce Customer Portal Incorrect Customer and Customer Group Frontend Menus pages visibility

## Summary
Severity: Medium
Advisory: GHSA-8gwj-68w6-7v6c
CVE: CVE-2023-32064
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-8gwj-68w6-7v6c
Type: github-advisory

## Affected
- Packagist: `oro/customer-portal` — affected >=4.2.0
- Packagist: `oro/customer-portal` — affected >=5.0.0 <5.0.11
- Packagist: `oro/customer-portal` — affected >=5.1.0 <5.1.1

## Details
Back-office users can access information about Customer and Customer User menus, bypassing ACL security restrictions due to insufficient security checks.

## References
- https://github.com/oroinc/orocommerce/security/advisories/GHSA-8gwj-68w6-7v6c
- https://nvd.nist.gov/vuln/detail/CVE-2023-32064
- https://github.com/oroinc/orocommerce
