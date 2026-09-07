# [C] SQL injection in phpMyAdmin

## Summary
Severity: Critical
Advisory: GHSA-jgjc-332c-8cmc
CVE: CVE-2019-18622
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-16
Source: https://github.com/advisories/GHSA-jgjc-332c-8cmc
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=0 <4.9.2

## Details
An issue was discovered in phpMyAdmin before 4.9.2. A crafted database/table name can be used to trigger a SQL injection attack through the designer feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18622
- https://github.com/phpmyadmin/composer/commit/51acbf53564d9b52e78509a5688ec2b68976b5f7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BA4DGF7KTQS6WA2DRNJSW66L43WB7LRV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W5GW4KEMNCBQYZCIXEJYC42OEBBN2NSH
- https://security.gentoo.org/glsa/202003-39
- https://www.phpmyadmin.net/security/PMASA-2019-5
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00024.html
