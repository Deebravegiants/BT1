# [M] Paymorrow Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-489x-ccjw-q7c4
CVE: CVE-2018-14020
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-489x-ccjw-q7c4
Type: github-advisory

## Affected
- Packagist: `oxid-esales/paymorrow-module` — affected >=1.0.0 <1.0.2
- Packagist: `oxid-esales/paymorrow-module` — affected >=2.0.0 <2.0.1

## Details
An issue was discovered in the Paymorrow module 1.0.0 before 1.0.2 and 2.0.0 before 2.0.1 for OXID eShop. An attacker can bypass delivery-address change detection if the payment module doesn't use eShop's checkout procedure properly. To do so, the attacker must change the delivery address to one that is not verified by the Paymorrow module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14020
- https://bugs.oxid-esales.com/view.php?id=6801
- https://github.com/OXID-eSales/paymorrow-module
- https://oxidforge.org/en/security-bulletin-2018-003.html
