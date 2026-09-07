# [M] OroCommerce Cross site scripting vulnerability during shipping rule editing for UPS integration

## Summary
Severity: Medium
Advisory: GHSA-4vf4-955g-vxp2
CVE: CVE-2022-31037
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-4vf4-955g-vxp2
Type: github-advisory

## Affected
- Packagist: `oro/commerce` — affected >=4.1.0 <5.0.6

## Details
### Impact
Shipping rule edit page is vulnerable to cross site scripting (XSS) payload added to UPS Surcharge field. The attacker should have permission to create or edit a shipping rule.

## References
- https://github.com/oroinc/orocommerce/security/advisories/GHSA-4vf4-955g-vxp2
- https://nvd.nist.gov/vuln/detail/CVE-2022-31037
- https://github.com/oroinc/orocommerce
