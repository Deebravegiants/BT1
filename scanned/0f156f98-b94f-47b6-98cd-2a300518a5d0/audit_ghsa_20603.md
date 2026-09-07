# [M] Improper Authentication in phpmyadmin

## Summary
Severity: Medium
Advisory: GHSA-8wf2-3ggj-78q9
CVE: CVE-2022-23807
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-8wf2-3ggj-78q9
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.9.0 <4.9.8
- Packagist: `phpmyadmin/phpmyadmin` — affected >=5.1.0 <5.1.2

## Details
An issue was discovered in phpMyAdmin 4.9 before 4.9.8 and 5.1 before 5.1.2. A valid user who is already authenticated to phpMyAdmin can manipulate their account to bypass two-factor authentication for future login instances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23807
- https://github.com/phpmyadmin/phpmyadmin/commit/ca54f1db050859eb8555875c6aa5d7796fdf4b32
- https://github.com/phpmyadmin/phpmyadmin
- https://security.gentoo.org/glsa/202311-17
- https://www.phpmyadmin.net/security/PMASA-2022-1
