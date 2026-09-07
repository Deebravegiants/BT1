# [M] phpMyAdmin XSS when checking tables

## Summary
Severity: Medium
Advisory: GHSA-222v-cx2c-q2f5
CVE: CVE-2025-24530
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-23
Source: https://github.com/advisories/GHSA-222v-cx2c-q2f5
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=5.0.0 <5.2.2

## Details
An issue was discovered in phpMyAdmin 5.x before 5.2.2. An XSS vulnerability has been discovered for the check tables feature. A crafted table or database name could be used for XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24530
- https://github.com/phpmyadmin/phpmyadmin/commit/23c13a81709728089ff031e5b1c29b5e91baa6a7
- https://github.com/phpmyadmin/phpmyadmin
- https://lists.debian.org/debian-lts-announce/2025/04/msg00016.html
- https://www.phpmyadmin.net/security/PMASA-2025-1
