# [C] The ADOdb sqlite3 driver allows SQL injection

## Summary
Severity: Critical
Advisory: GHSA-vf2r-cxg9-p7rf
CVE: CVE-2025-54119
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-vf2r-cxg9-p7rf
Type: github-advisory

## Affected
- Packagist: `adodb/adodb-php` — affected >=0 <5.22.10

## Details
Improper escaping of a query parameter may allow an attacker to execute arbitrary SQL statements when the code using ADOdb connects to a sqlite3 database and calls the metaColumns(), metaForeignKeys() or metaIndexes() methods with a crafted table name.

Note that the indicated Severity corresponds to a worst-case usage scenario, e.g. allowing user-supplied data to be sent as-is to the above-mentioned methods.

### Impact
SQLite3 driver.

### Patches
Vulnerability is fixed in ADOdb 5.22.10 (https://github.com/ADOdb/ADOdb/commit/5b8bd52cdcffefb4ecded1b399c98cfa516afe03).

### Workarounds
Only pass controlled data to metaColumns(), metaForeignKeys() and metaIndexes() method's $table parameter.

### Credits

Thanks to Marco Nappi (@mrcnpp) for reporting this vulnerability.

## References
- https://github.com/ADOdb/ADOdb/security/advisories/GHSA-vf2r-cxg9-p7rf
- https://nvd.nist.gov/vuln/detail/CVE-2025-54119
- https://github.com/ADOdb/ADOdb/issues/1083
- https://github.com/ADOdb/ADOdb/commit/5b8bd52cdcffefb4ecded1b399c98cfa516afe03
- https://github.com/ADOdb/ADOdb
- https://lists.debian.org/debian-lts-announce/2025/10/msg00020.html
