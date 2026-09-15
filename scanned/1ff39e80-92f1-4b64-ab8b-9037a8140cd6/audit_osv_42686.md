# [H] Koha - SQL Injection in reports/acquisitions_stats.pl

## Summary
Severity: High
Advisory: CVE-2026-70369
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70369
Type: osv

## Details
Koha's reports/acquisitions_stats.pl builds its per-cell statistics query in sub calculate by interpolating the user-controlled Filter request parameters directly into WHERE fragments covering aqbasket.closedate, aqorders.datereceived, aqbooksellers.name, items.homebranch, items.ccode, biblioitems.itemtype, aqbudgets.budget_code, aqorders.sort1, and aqorders.sort2.

## References
- https://koha-community.org/
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=42360
- https://download.koha-community.org/koha-25.05.12.tar.gz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70369.json
- https://koha-community.org/koha-25-05-12-released/
- https://nvd.nist.gov/vuln/detail/CVE-2026-70369
- https://gitlab.com/koha-community/Koha
