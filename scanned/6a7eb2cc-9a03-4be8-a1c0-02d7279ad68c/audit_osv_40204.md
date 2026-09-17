# [M] CVE-2026-50812

## Summary
Severity: Medium
Advisory: CVE-2026-50812
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-50812
Type: osv

## Details
A NULL pointer dereference in the SQLite Session Extension in SQLite 3.53.1 and SQLite trunk builds before check-in e807d4e3798efd53 allows an attacker who can supply a malformed changeset blob to cause a denial of service. The issue occurs when sqlite3changeset_apply_v3() applies a corrupt changeset and reaches sqlite3_value_type() with a NULL sqlite3_value pointer.

## References
- https://gist.github.com/junius-sec/bb556f333957c5226dede314db0e9e91
- https://sqlite.org/src/info/e807d4e3798efd53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50812.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50812
- https://github.com/sqlite/sqlite/commit/b869ed6b067d623cb1383549f2a18aa35508385d
