# [H] phpMyAdmin Improper Authentication

## Summary
Severity: High
Advisory: GHSA-x394-g9j8-x7mf
CVE: CVE-2018-12613
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x394-g9j8-x7mf
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.8 <4.8.2

## Details
An issue was discovered in phpMyAdmin 4.8.x before 4.8.2, in which an attacker can include (view and potentially execute) files on the server. The vulnerability comes from a portion of code where pages are redirected and loaded within phpMyAdmin, and an improper test for whitelisted pages. An attacker must be authenticated, except in the "$cfg['AllowArbitraryServer'] = true" case (where an attacker can specify any host he/she is already in control of, and execute arbitrary code on phpMyAdmin) and the "$cfg['ServerDefault'] = 0" case (which bypasses the login requirement and runs the vulnerable code without any authentication).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12613
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201904-16
- https://www.exploit-db.com/exploits/44924
- https://www.exploit-db.com/exploits/44928
- https://www.exploit-db.com/exploits/45020
- https://www.phpmyadmin.net/security/PMASA-2018-4
- http://packetstormsecurity.com/files/164623/phpMyAdmin-4.8.1-Remote-Code-Execution.html
- http://www.securityfocus.com/bid/104532
