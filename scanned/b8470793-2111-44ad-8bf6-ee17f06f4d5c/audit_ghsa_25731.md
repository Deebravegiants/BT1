# [H] Exposure of Sensitive Information to an Unauthorized Actor in PhpMyAdmin

## Summary
Severity: High
Advisory: GHSA-vx8q-j7h9-vf6q
CVE: CVE-2022-0813
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-vx8q-j7h9-vf6q
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <5.1.3

## Details
PhpMyAdmin before 5.1.3 allows an attacker to retrieve potentially sensitive information by creating invalid requests. This affects the lang parameter, the pma_parameter, and the cookie section.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0813
- https://security.gentoo.org/glsa/202311-17
- https://www.phpmyadmin.net/news/2022/2/11/phpmyadmin-4910-and-513-are-released
