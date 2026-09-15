# [M] Cross-Site Request Forgery in CakePHP

## Summary
Severity: Medium
Advisory: GHSA-j33j-fg2g-mcv2
CVE: CVE-2020-15400
CWE: CWE-352, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-j33j-fg2g-mcv2
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=4.0.0 <4.0.6
- Packagist: `cakephp/cakephp` — affected >=0 <3.10.3

## Details
CakePHP before 4.0.6 and 3.10.3 mishandles CSRF token generation. This might be remotely exploitable in conjunction with XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15400
- https://bakery.cakephp.org/2020/04/18/cakephp_406_released.html
- https://bakery.cakephp.org/2022/05/08/cakephp_3103_released.html
