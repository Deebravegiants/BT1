# [M] BIT-sqlite-2021-45346

## Summary
Severity: Medium
Advisory: BIT-sqlite-2021-45346
Aliases: CVE-2021-45346
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2021-45346
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.37.0 <3.37.1

## Details
A Memory Leak vulnerability exists in SQLite Project SQLite3 3.35.1 and 3.37.0 via maliciously crafted SQL Queries (made via editing the Database File), it is possible to query a record, and leak subsequent bytes of memory that extend beyond the record, which could let a malicious user obtain sensitive information. NOTE: The developer disputes this as a vulnerability stating that If you give SQLite a corrupted database file and submit a query against the database, it might read parts of the database that you did not intend or expect.

## References
- https://github.com/guyinatuxedo/sqlite3_record_leaking
- https://security.netapp.com/advisory/ntap-20220303-0001/
- https://sqlite.org/forum/forumpost/056d557c2f8c452ed5
- https://sqlite.org/forum/forumpost/53de8864ba114bf6
- https://www.sqlite.org/cves.html#status_of_recent_sqlite_cves
- https://nvd.nist.gov/vuln/detail/CVE-2021-45346
