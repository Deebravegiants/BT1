# [C] Fix a use-after-free bug in diesels Sqlite backend

## Summary
Severity: Critical
Advisory: GHSA-j8q9-5rp9-4mv9
CVE: CVE-2021-28305
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j8q9-5rp9-4mv9
Type: github-advisory

## Affected
- crates.io: `diesel` — affected >=0 <1.4.6

## Details
An issue was discovered in the diesel crate before 1.4.6 for Rust. There is a use-after-free in the SQLite backend because the semantics of sqlite3_column_name are not followed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28305
- https://github.com/diesel-rs/diesel/pull/2663
- https://github.com/diesel-rs/diesel
- https://rustsec.org/advisories/RUSTSEC-2021-0037.html
