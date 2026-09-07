# [M] Reflected XSS with parameters in PostComment

## Summary
Severity: Medium
Advisory: GHSA-58w4-w77w-qv3w
CVE: CVE-2020-26225
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-11-16
Source: https://github.com/advisories/GHSA-58w4-w77w-qv3w
Type: github-advisory

## Affected
- Packagist: `prestashop/productcomments` — affected >=4.0.0 <4.2.0

## Details
### Impact
An attacker could inject malicious web code into the users' web browsers by creating a malicious link.

### Patches
The problem is fixed in 4.2.0

### References
[Cross-site Scripting (XSS) - Reflected (CWE-79) ](https://cwe.mitre.org/data/definitions/79.html)

## References
- https://github.com/PrestaShop/productcomments/security/advisories/GHSA-58w4-w77w-qv3w
- https://nvd.nist.gov/vuln/detail/CVE-2020-26225
- https://github.com/PrestaShop/productcomments/commit/c56e3e9495c4a0a9c1e7dc43e1bb0fcad2796dbf
