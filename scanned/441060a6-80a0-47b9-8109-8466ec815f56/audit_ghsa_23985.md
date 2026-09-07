# [M] phpMyAdmin Improper Input Validation

## Summary
Severity: Medium
Advisory: GHSA-w8qg-j9fp-hrjf
CVE: CVE-2016-2562
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w8qg-j9fp-hrjf
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.5 <4.5.5.1

## Details
The checkHTTP function in libraries/Config.class.php in phpMyAdmin 4.5.x before 4.5.5.1 does not verify X.509 certificates from api.github.com SSL servers, which allows man-in-the-middle attackers to spoof these servers and obtain sensitive information via a crafted certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2562
- https://github.com/phpmyadmin/phpmyadmin/commit/e42b7e3aedd29dd0f7a48575f20bfc5aca0ff976
- https://github.com/phpmyadmin/composer
- https://www.phpmyadmin.net/security/PMASA-2016-13
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178562.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178869.html
