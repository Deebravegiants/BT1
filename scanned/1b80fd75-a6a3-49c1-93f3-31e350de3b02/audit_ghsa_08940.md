# [H] Diesel's SQLite backend has possible UTF-8 corruption

## Summary
Severity: High
Advisory: GHSA-h5x4-m2qf-r4f2
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-h5x4-m2qf-r4f2
Type: github-advisory

## Affected
- crates.io: `diesel` — affected >=0 <2.3.8

## Details
Diesel uses the `sqlite3_value_text` function to receive strings from SQLite while deserializing query results. We misinterpreted the corresponding [SQLite](https://sqlite.org/c3ref/value_blob.html) documentation that this function always returns a UTF-8 encoded string values as `*const c_char`. Based on that we used `str::from_utf8_unchecked` to construct a Rust string slice without any additional UTF-8 checks in place. It turned out that this function doesn't always return correct UTF-8 strings. For field of the SQLite side storage type `BLOB` this pointer can contain arbitrary bytes, which makes the usage of `str::from_utf8_unchecked` unsound as this violates the safety contract of `str` to only contain valid UTF-8 encoded Strings.

## Mitigation

The preferred mitigation to the outlined problem is to update to a Diesel version 2.3.8 or newer, which includes fixes for the problem.

## Resolution

Diesel now correctly checks whether the provides byte buffer is actually valid UTF-8, instead of relying on SQLite's documentation. This fix is included in the `2.3.8` release.

## References
- https://github.com/diesel-rs/diesel/pull/5042
- https://github.com/diesel-rs/diesel
- https://rustsec.org/advisories/RUSTSEC-2026-0111.html
