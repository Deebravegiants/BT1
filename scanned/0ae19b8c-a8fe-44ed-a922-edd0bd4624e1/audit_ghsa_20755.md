# [M] PrestaShop Product Comments Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-prrh-qvhf-x788
CVE: CVE-2022-35933
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-31
Source: https://github.com/advisories/GHSA-prrh-qvhf-x788
Type: github-advisory

## Affected
- Packagist: `prestashop/productcomments` — affected >=0 <5.0.2

## Details
### Impact
An attacker could steal an admin's cookie

### Patches
The issue is fixed in 5.0.2

### References
[Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')](https://cwe.mitre.org/data/definitions/79.html)

## References
- https://github.com/PrestaShop/productcomments/security/advisories/GHSA-prrh-qvhf-x788
- https://nvd.nist.gov/vuln/detail/CVE-2022-35933
- https://github.com/PrestaShop/productcomments/commit/314456d739155aa71f0b235827e8e0f24b97c26b
- https://github.com/PrestaShop/productcomments
