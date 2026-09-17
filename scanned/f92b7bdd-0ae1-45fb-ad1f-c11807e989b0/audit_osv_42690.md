# [H] Koha - SQL Injection in reports/issues_stats.pl

## Summary
Severity: High
Advisory: CVE-2026-70373
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70373
Type: osv

## Details
Koha's reports/issues_stats.pl (the circulation statistics report) builds its calculation query in sub calculate by concatenating several user-controlled request parameters directly into the SQL string. The PeriodTypeSel, PeriodDaySel, and PeriodMonthSel parameters are interpolated raw into single-quoted equality and function-comparison fragments, and the Filter slots plus the Line and Column identifiers are likewise interpolated with no whitelist and no placeholder binding.

## References
- https://koha-community.org/
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=42735
- https://download.koha-community.org/koha-25.05.12.tar.gz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70373.json
- https://koha-community.org/koha-25-05-12-released/
- https://nvd.nist.gov/vuln/detail/CVE-2026-70373
- https://gitlab.com/koha-community/Koha
