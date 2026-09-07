# [M] Stored XSS with custom URLs in PrestaShop module ps_linklist

## Summary
Severity: Medium
Advisory: GHSA-cx2r-mf6x-55rx
CVE: CVE-2020-5273
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-cx2r-mf6x-55rx
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_linklist` — affected >=0 <3.1.0

## Details
### Impact
Stored XSS when using custom URLs.

### Patches
The problem is fixed in 3.1.0

### References
[Cross-site Scripting (XSS) - Stored (CWE-79)](https://cwe.mitre.org/data/definitions/79.html)

## References
- https://github.com/PrestaShop/ps_linklist/security/advisories/GHSA-cx2r-mf6x-55rx
- https://nvd.nist.gov/vuln/detail/CVE-2020-5273
- https://github.com/PrestaShop/ps_linklist/commit/83e6e0bdda2287f4d6e64127cb90c41d26b5ad82
- https://github.com/PrestaShop/ps_linklist
