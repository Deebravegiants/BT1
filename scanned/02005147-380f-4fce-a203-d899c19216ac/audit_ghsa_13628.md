# [M] OroCommerce Cross-site Scripting vulnerability in add note dialog of Shopping List line item

## Summary
Severity: Medium
Advisory: GHSA-2jc6-3fhj-8q84
CVE: CVE-2022-35950
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-2jc6-3fhj-8q84
Type: github-advisory

## Affected
- Packagist: `oro/commerce` — affected >=4.1.0
- Packagist: `oro/commerce` — affected >=4.2.0
- Packagist: `oro/commerce` — affected >=5.0.0 <5.0.11
- Packagist: `oro/commerce` — affected >=5.1.0 <5.1.1

## Details
### Impact

The JS payload added to the product name may be executed at the storefront when adding a note to the shopping list line item containing a vulnerable product.
An attacker should be able to edit a product in the admin area and force a user to add this product to Shopping List and click add a note for it.

## References
- https://github.com/oroinc/orocommerce/security/advisories/GHSA-2jc6-3fhj-8q84
- https://nvd.nist.gov/vuln/detail/CVE-2022-35950
- https://github.com/oroinc/orocommerce
