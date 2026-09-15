# [C] Use-after-free in yottadb

## Summary
Severity: Critical
Advisory: GHSA-9658-c26v-7qvf
CVE: CVE-2021-27377
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9658-c26v-7qvf
Type: github-advisory

## Affected
- crates.io: `yottadb` — affected >=0 <1.2.0

## Details
An issue was discovered in the yottadb crate before 1.2.0 for Rust. For some memory-allocation patterns, ydb_subscript_next_st and ydb_subscript_prev_st have a use-after-free.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27377
- https://gitlab.com/YottaDB/Lang/YDBRust
- https://gitlab.com/YottaDB/Lang/YDBRust/-/issues/40
- https://rustsec.org/advisories/RUSTSEC-2021-0022.html
