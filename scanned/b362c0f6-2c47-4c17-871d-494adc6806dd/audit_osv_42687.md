# [H] Koha - SQL Injection in reports/catalogue_stats.pl

## Summary
Severity: High
Advisory: CVE-2026-70370
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70370
Type: osv

## Details
Koha's reports/catalogue_stats.pl builds dynamic SQL in sub calculate by interpolating the user-controlled Line and Column request parameters directly into identifier positions of the query (SELECT DISTINCTROW, GROUP BY, ORDER BY) with no whitelist validation.

## References
- https://koha-community.org/
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=42363
- https://download.koha-community.org/koha-25.05.12.tar.gz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70370.json
- https://koha-community.org/koha-25-05-12-released/
- https://nvd.nist.gov/vuln/detail/CVE-2026-70370
- https://gitlab.com/koha-community/Koha
