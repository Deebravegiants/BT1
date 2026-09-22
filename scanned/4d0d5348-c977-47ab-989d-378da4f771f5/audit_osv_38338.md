# [M] CVE-2026-39113

## Summary
Severity: Medium
Advisory: CVE-2026-39113
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-39113
Type: osv

## Details
Buffer Overflow vulnerability in SQLite affected version source snapshots/builds containing Fossil check-in 8bdc0d485e3ad0c7a1e818da66f106951d496b05cbe61d12c2c448f2f24b6d5d (Git mirror 169f68ed88b34cb68f720191c64c058f2ccec508, 2026-03-11) and later snapshots/builds allows an attacker to cause a denial of service via the ext/misc/sqlar.c, sqlarUncompressFunc(), sqlar_uncompress(), sqlite3_value_int64(), sqlite3_malloc(int), uncompress() components

## References
- https://github.com/sqlite/sqlite/blob/169f68ed88b34cb68f720191c64c058f2ccec508/ext/misc/sqlar.c
- https://www.sqlite.org/
- https://www.sqlite.org/sqlar.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39113
- https://github.com/sqlite/sqlite/commit/169f68ed88b34cb68f720191c64c058f2ccec508
- https://github.com/20000419/CVE-2026-39113
