# [H] Koha - SQL Injection in reports/issues_avg_stats.pl

## Summary
Severity: High
Advisory: CVE-2026-70371
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70371
Type: osv

## Details
Koha's reports/issues_avg_stats.pl builds dynamic SQL in sub calculate by concatenating several user-controlled request parameters directly into the query string. The Line and Column parameters are not validated against any whitelist and land verbatim in identifier positions (SELECT DISTINCTROW, GROUP BY, ORDER BY), and each Filter slot is concatenated raw into single-quoted LIKE, BETWEEN, and comparison fragments with no bound parameters.

## References
- https://koha-community.org/
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=42368
- https://download.koha-community.org/koha-25.05.12.tar.gz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70371.json
- https://koha-community.org/koha-25-05-12-released/
- https://nvd.nist.gov/vuln/detail/CVE-2026-70371
- https://gitlab.com/koha-community/Koha
