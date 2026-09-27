# [C] SQL injection in ADOdb PostgreSQL driver pg_insert_id() method

## Summary
Severity: Critical
Advisory: GHSA-8x27-jwjr-8545
CVE: CVE-2025-46337
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-05-01
Source: https://github.com/advisories/GHSA-8x27-jwjr-8545
Type: github-advisory

## Affected
- Packagist: `adodb/adodb-php` — affected >=0 <5.22.9

## Details
Improper escaping of a query parameter may allow an attacker to execute arbitrary SQL statements when the code using ADOdb connects to a PostgreSQL database and calls pg_insert_id() with user-supplied data.

Note that the indicated Severity corresponds to a worst-case usage scenario.

### Impact
PostgreSQL drivers (postgres64, postgres7, postgres8, postgres9).

### Patches
Vulnerability is fixed in ADOdb 5.22.9 (11107d6d6e5160b62e05dff8a3a2678cf0e3a426).

### Workarounds
Only pass controlled data to pg_insert_id() method's $fieldname parameter, or escape it with pg_escape_identifier() first.

### References
- Issue https://github.com/ADOdb/ADOdb/issues/1070
- [Blog post](https://xaliom.blogspot.com/2025/05/from-sast-to-cve-2025-46337.html) by Marco Nappi

### Credits
Thanks to Marco Nappi (@mrcnpp) for reporting this vulnerability.

## References
- https://github.com/ADOdb/ADOdb/security/advisories/GHSA-8x27-jwjr-8545
- https://nvd.nist.gov/vuln/detail/CVE-2025-46337
- https://github.com/ADOdb/ADOdb/issues/1070
- https://github.com/ADOdb/ADOdb/commit/11107d6d6e5160b62e05dff8a3a2678cf0e3a426
- https://github.com/ADOdb/ADOdb
- https://lists.debian.org/debian-lts-announce/2025/05/msg00029.html
- https://xaliom.blogspot.com/2025/05/from-sast-to-cve-2025-46337.html
