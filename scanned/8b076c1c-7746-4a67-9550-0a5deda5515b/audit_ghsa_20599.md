# [H] Sandbox bypass in Latte templates

## Summary
Severity: High
Advisory: GHSA-36m2-8rhx-f36j
CVE: CVE-2022-21648
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-36m2-8rhx-f36j
Type: github-advisory

## Affected
- Packagist: `latte/latte` — affected >=2.10.0 <2.10.8
- Packagist: `latte/latte` — affected >=2.9.0 <2.9.6
- Packagist: `latte/latte` — affected >=2.8.0 <2.8.8

## Details
### Impact
The problem affects users who use the sandbox in Latte and templates from untrusted sources.

### Patches
Sandbox first appeared in Latte 2.8.0. The issue is fixed in the versions 2.8.8, 2.9.6 and 2.10.8. 

### References
The issues were discovered by
- JinYiTong (https://github.com/JinYiTong)
- 赵钰迪 <20212010122@fudan.edu.cn>

## References
- https://github.com/nette/latte/security/advisories/GHSA-36m2-8rhx-f36j
- https://nvd.nist.gov/vuln/detail/CVE-2022-21648
- https://github.com/nette/latte/commit/9e1b4f7d70f7a9c3fa6753ffa7d7e450a3d4abb0
- https://github.com/nette/latte
