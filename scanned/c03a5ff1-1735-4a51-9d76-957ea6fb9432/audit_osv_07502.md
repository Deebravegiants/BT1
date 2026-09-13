# [H] SQLite SQLite3 make alltest sqlite3session.c sessionReadRecord heap-based overflow

## Summary
Severity: High
Advisory: BIT-sqlite-2023-7104
Aliases: CVE-2023-7104
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2023-7104
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.43.1

## Details
A vulnerability was found in SQLite SQLite3 up to 3.43.0 and classified as critical. This issue affects the function sessionReadRecord of the file ext/session/sqlite3session.c of the component make alltest Handler. The manipulation leads to heap-based buffer overflow. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-248999.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AYONA2XSNFMXLAW4IHLFI5UVV3QRNG5K/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D6C2HN4T2S6GYNTAUXLH45LQZHK7QPHP/
- https://security.netapp.com/advisory/ntap-20240112-0008/
- https://sqlite.org/forum/forumpost/5bcbf4571c
- https://sqlite.org/src/info/0e4e7a05c4204b47
- https://vuldb.com/?ctiid.248999
- https://vuldb.com/?id.248999
- https://nvd.nist.gov/vuln/detail/CVE-2023-7104
- https://lists.debian.org/debian-lts-announce/2024/09/msg00050.html
