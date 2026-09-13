# [H] Koha - SQL Injection in reports/bor_issues_top.pl

## Summary
Severity: High
Advisory: CVE-2026-70372
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70372
Type: osv

## Details
Koha's reports/bor_issues_top.pl builds dynamic SQL in sub calculate by concatenating several user-controlled request parameters directly into the query string. An authenticated staff user holding the reports module permission can inject arbitrary SQL and read any table reachable by the Koha database user, including borrowers (password hashes, two-factor secrets, personal data), api_keys, and sessions.

## References
- https://koha-community.org/
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=42369
- https://download.koha-community.org/koha-25.05.12.tar.gz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70372.json
- https://koha-community.org/koha-25-05-12-released/
- https://nvd.nist.gov/vuln/detail/CVE-2026-70372
- https://gitlab.com/koha-community/Koha
