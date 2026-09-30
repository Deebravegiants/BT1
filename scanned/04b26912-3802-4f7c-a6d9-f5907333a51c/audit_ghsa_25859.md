# [C] Code Injection in PHPUnit

## Summary
Severity: Critical
Advisory: GHSA-r7c9-c69m-rph8
CVE: CVE-2017-9841
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-r7c9-c69m-rph8
Type: github-advisory

## Affected
- Packagist: `phpunit/phpunit` — affected >=4.8.19 <4.8.28
- Packagist: `phpunit/phpunit` — affected >=5.0.10 <5.6.3

## Details
Util/PHP/eval-stdin.php in PHPUnit starting with 4.8.19 and before 4.8.28, as well as 5.x before 5.6.3, allows remote attackers to execute arbitrary PHP code via HTTP POST data beginning with a `<?php ` substring, as demonstrated by an attack on a site with an exposed /vendor folder, i.e., external access to the /vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9841
- https://github.com/sebastianbergmann/phpunit/pull/1955
- https://github.com/sebastianbergmann/phpunit/pull/1956
- https://github.com/sebastianbergmann/phpunit/commit/284a69fb88a2d0845d23f42974a583d8f59bf5a5
- https://github.com/sebastianbergmann/phpunit/commit/3aaddb1c5bd9b9b8d070b4cf120e71c36fd08412
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpunit/phpunit/CVE-2017-9841.yaml
- https://github.com/sebastianbergmann/phpunit
- https://security.gentoo.org/glsa/201711-15
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-9841
- https://www.oracle.com/security-alerts/cpuoct2021.html
- http://web.archive.org/web/20170701212357/http://phpunit.vulnbusters.com
- http://www.securityfocus.com/bid/101798
- http://www.securitytracker.com/id/1039812
