# [M] phpMyAdmin XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3q28-xfw3-2q35
CVE: CVE-2016-5732
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3q28-xfw3-2q35
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the partition-range implementation in `templates/table/structure/display_partitions.phtml` in the table-structure page in phpMyAdmin 4.6.x before 4.6.3 allow remote attackers to inject arbitrary web script or HTML via crafted table parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5732
- https://github.com/phpmyadmin/phpmyadmin/commit/0815af37f483f329f0c0565d68821fea9c47b5f5
- https://github.com/phpmyadmin/phpmyadmin/commit/792cd1262f012b9b13639519d414f2acaeb5e972
- https://github.com/phpmyadmin/phpmyadmin
- https://security.gentoo.org/glsa/201701-32
- https://www.phpmyadmin.net/security/PMASA-2016-25
