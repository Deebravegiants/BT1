# [M] phpMyAdmin CRLF Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wj42-52pv-wfj2
CVE: CVE-2005-3621
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-wj42-52pv-wfj2
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <2.6.4-pl4

## Details
CRLF injection vulnerability in phpMyAdmin before 2.6.4-pl4 allows remote attackers to conduct HTTP response splitting attacks via unspecified scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-3621
- https://web.archive.org/web/20060514052317/http://securitytracker.com/alerts/2005/Nov/1015213.html
- https://web.archive.org/web/20061015000000*/http://www.novell.com/linux/security/advisories/2005_28_sr.html
- https://www.debian.org/security/2006/dsa-1207
- https://www.phpmyadmin.net/home_page/security.php?issue=PMASA-2005-6
