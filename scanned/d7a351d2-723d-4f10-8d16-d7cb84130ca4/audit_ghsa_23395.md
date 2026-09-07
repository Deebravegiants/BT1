# [M] SCart is vulnerable to cross-site scripting (XSS) 

## Summary
Severity: Medium
Advisory: GHSA-7pfc-cx3m-v22x
CVE: CVE-2022-21149
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-7pfc-cx3m-v22x
Type: github-advisory

## Affected
- Packagist: `s-cart/core` — affected >=0 <6.9
- Packagist: `s-cart/s-cart` — affected >=0 <6.9

## Details
SCart e-commerce is a free open source for businesses, built on the Laravel framework. The package s-cart/s-cart before 6.9 and the package s-cart/core before 6.9 are vulnerable to cross-site Scripting (XSS) which can lead to cookie stealing of any victim that visits the affected URL. An attacker can gain unauthorized access to that user's account through the stolen cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21149
- https://github.com/s-cart/core
- https://snyk.io/vuln/SNYK-PHP-SCARTCORE-2389036
- https://snyk.io/vuln/SNYK-PHP-SCARTSCART-2389035
