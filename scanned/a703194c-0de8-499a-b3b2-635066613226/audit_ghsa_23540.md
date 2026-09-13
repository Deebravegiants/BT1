# [H] CakePHP allows remote attackers to spoof their IP

## Summary
Severity: High
Advisory: GHSA-j8p3-8m69-2hqq
CVE: CVE-2016-4793
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j8p3-8m69-2hqq
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=1.2.0 <2.6.13
- Packagist: `cakephp/cakephp` — affected >=2.7.0-rc1 <2.7.11
- Packagist: `cakephp/cakephp` — affected >=2.8.0-rc1 <2.8.2
- Packagist: `cakephp/cakephp` — affected >=3.0.0-rc1 <3.0.17
- Packagist: `cakephp/cakephp` — affected >=3.1.0-beta1 <3.1.12
- Packagist: `cakephp/cakephp` — affected >=3.2.0-rc1 <3.2.5

## Details
The `clientIp` function in CakePHP 3.2.4 and earlier allows remote attackers to spoof their IP via the `CLIENT-IP HTTP` header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4793
- https://github.com/cakephp/cakephp/commit/908754649f70bab2b1093942e17c9a46a2fcf6c2
- https://bakery.cakephp.org/2016/03/13/cakephp_2613_2711_282_3017_3112_325_released.html
- https://github.com/cakephp/cakephp
- https://support.citrix.com/article/CTX236992
- https://www.exploit-db.com/exploits/39813
- http://legalhackers.com/advisories/CakePHP-IP-Spoofing-Vulnerability.txt
- http://www.securityfocus.com/bid/95846
