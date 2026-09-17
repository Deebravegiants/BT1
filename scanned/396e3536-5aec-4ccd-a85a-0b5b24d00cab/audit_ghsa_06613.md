# [M] Diesel has possible use after free when deserializing a SQLite database via `SqliteConnection::deserialize_readonly_database`

## Summary
Severity: Medium
Advisory: GHSA-ggxf-9f6j-w742
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-ggxf-9f6j-w742
Type: github-advisory

## Affected
- crates.io: `diesel` — affected >=0 <2.3.10

## Details
Diesel allows loading a SQLite database from a byte buffer, represented as `&[u8]`, at runtime via the `SqliteConnection::deserialize_readonly_database` function. In previous versions of Diesel, this buffer was passed directly to libsqlite3. Since libsqlite3 requires the buffer to remain alive for as long as the database connection is open and Diesel did not ensure this as part of its safe API, callers of `SqliteConnection::deserialize_readonly_database` could drop the buffer prematurely. This prematurely drop caused libsqlite3 to operate on freed memory.

This vulnerability affects users of `SqliteConnection::deserialize_readonly_database` who drop the buffer passed to the function before they drop the database connection.

## Mitigation

The preferred mitigation to the outlined problem is to update to Diesel version 2.3.10 or newer, which includes a fix for the problem. Alternatively users need to take to keep the buffer alive until the connection is dropped.

## Resolution

Diesel now stores a copy of the buffer inside of the `SqliteConnection` object itself to keep it alive as long as the underlying libsqlite3 connection exists.

## References
- https://github.com/diesel-rs/diesel/commit/1bc2ea46d9840e8d9af844239d3c84f37fe7d84b
- https://github.com/diesel-rs/diesel
- https://rustsec.org/advisories/RUSTSEC-2026-0172.html
