# [M] phpMyAdmin Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-3hw5-fffc-qrg4
CVE: CVE-2016-9860
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3hw5-fffc-qrg4
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.9
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.18

## Details
An issue was discovered in phpMyAdmin. An unauthenticated user can execute a denial of service attack when phpMyAdmin is running with $cfg['AllowArbitraryServer']=true. All 4.6.x versions (prior to 4.6.5), 4.4.x versions (prior to 4.4.15.9), and 4.0.x versions (prior to 4.0.10.18) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9860
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-65
- http://www.securityfocus.com/bid/94525
