# [M] zend-diactoros Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-rh3c-7wqx-6w95
CVE: CVE-2015-3257
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rh3c-7wqx-6w95
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-diactoros` — affected >=1.0.0 <1.0.4

## Details
`Zend/Diactoros/Uri::filterPath` in zend-diactoros before 1.0.4 does not properly sanitize path input, which allows remote attackers to perform cross-site scripting (XSS) or open redirect attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3257
- https://framework.zend.com/security/advisory/ZF2015-05
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-diactoros/CVE-2015-3257.yaml
- https://github.com/zendframework/zend-diactoros
- http://www.securityfocus.com/bid/75466
