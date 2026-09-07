# [H] phpMyAdmin CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-f9hx-5jq4-fgjm
CVE: CVE-2017-1000499
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f9hx-5jq4-fgjm
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.7 <4.7.7

## Details
phpMyAdmin versions 4.7.x (prior to 4.7.6.1/4.7.7) are vulnerable to a CSRF weakness. By deceiving a user to click on a crafted URL, it is possible to perform harmful database operations such as deleting records, dropping/truncating tables etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000499
- https://web.archive.org/web/20201208204518/http://www.securitytracker.com/id/1040163
- https://www.exploit-db.com/exploits/45284
- https://www.phpmyadmin.net/security/PMASA-2017-9
- http://cyberworldmirror.com/vulnerability-phpmyadmin-lets-attacker-perform-drop-table-single-click
