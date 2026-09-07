# [H] Potential XSS injection In PrestaShop contactform

## Summary
Severity: High
Advisory: GHSA-95hx-62rh-gg96
CVE: CVE-2020-15178
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-09-15
Source: https://github.com/advisories/GHSA-95hx-62rh-gg96
Type: github-advisory

## Affected
- Packagist: `prestashop/contactform` — affected >=1.0.1 <4.3.0

## Details
### Impact
An attacker is able to inject javascript while using the contact form. 

### Patches
The problem is fixed in v4.3.0

### References
[Cross-site Scripting (XSS) - Stored (CWE-79)](https://cwe.mitre.org/data/definitions/79.html)

## References
- https://github.com/PrestaShop/contactform/security/advisories/GHSA-95hx-62rh-gg96
- https://nvd.nist.gov/vuln/detail/CVE-2020-15178
- https://github.com/PrestaShop/contactform/commit/a1da814bea7e5750b858a2dbbc58ace80379f42f
- https://github.com/PrestaShop/contactform/commit/ecd9f5d14920ec00885766a7cb41bcc5ed8bfa09
- https://github.com/PrestaShop/contactform
- https://packagist.org/packages/prestashop/contactform
