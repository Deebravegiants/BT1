# [H] CVE-2026-21641

## Summary
Severity: High
Advisory: CVE-2026-21641
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2026-21641
Type: osv

## Details
HackerOne community member Jad Ghamloush (0xjad) has reported an authorization bypass vulnerability in the `tracker-delete.php` script of Revive Adserver. Users with permissions to delete trackers are mistakenly allowed to delete trackers owned by other accounts.

## References
- https://hackerone.com/reports/3445710
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-21641
