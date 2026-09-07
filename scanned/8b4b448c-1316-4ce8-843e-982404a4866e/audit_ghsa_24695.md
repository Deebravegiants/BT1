# [H] phpMyAdmin SQL Injection

## Summary
Severity: High
Advisory: GHSA-h65r-8fp8-w7cx
CVE: CVE-2020-10804
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h65r-8fp8-w7cx
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.9.0 <4.9.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=5.0.0 <5.0.2

## Details
In phpMyAdmin 4.x before 4.9.5 and 5.x before 5.0.2, a SQL injection vulnerability was found in retrieval of the current username (in libraries/classes/Server/Privileges.php and libraries/classes/UserPassword.php). A malicious user with access to the server could create a crafted username, and then trick the victim into performing specific actions with that user account (such as editing its privileges).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10804
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmyadmin/phpmyadmin/CVE-2020-10804.yaml
- https://github.com/phpmyadmin/composer
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AAVW3SUKWR5RF5LZ6SARCYOWBIFUIWOJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BUG3IRITW2LUBGR5LSQMP7MVRTELHZJK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UZI6EQVRRIG252DY3MBT33BJVCSYDMQO
- https://www.phpmyadmin.net/security/PMASA-2020-2
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00005.html
