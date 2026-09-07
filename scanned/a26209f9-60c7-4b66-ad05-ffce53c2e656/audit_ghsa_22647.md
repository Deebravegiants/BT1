# [H] phpMyAdmin Denial Of Service (DOS) attack

## Summary
Severity: High
Advisory: GHSA-9rmm-8fp4-26hv
CVE: CVE-2016-5706
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9rmm-8fp4-26hv
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.0 <4.0.10.16
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4 <4.4.15.7
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6 <4.6.3

## Details
js/get_scripts.js.php in phpMyAdmin 4.0.x before 4.0.10.16, 4.4.x before 4.4.15.7, and 4.6.x before 4.6.3 allows remote attackers to cause a denial of service via a large array in the scripts parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5706
- https://github.com/phpmyadmin/phpmyadmin/commit/4767f24ea4c1e3822ce71a636c341e8ad8d07aa6
- https://github.com/phpmyadmin/phpmyadmin/commit/805225a28c1428d7809e613c731c2126960e98df
- https://github.com/phpmyadmin/phpmyadmin/commit/abb3685c8702de887988fee31a97ef4d80d856a1
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-22
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00113.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00114.html
- http://www.debian.org/security/2016/dsa-3627
- http://www.securityfocus.com/bid/91376
