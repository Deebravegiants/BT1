# [H] Data races in scottqueue

## Summary
Severity: High
Advisory: GHSA-gvvv-w559-2hg6
CVE: CVE-2020-36453
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gvvv-w559-2hg6
Type: github-advisory

## Affected
- crates.io: `scottqueue` — affected >=0

## Details
An issue was discovered in the scottqueue crate through 2020-11-15 for Rust. There are unconditional implementations of Send and Sync for Queue<T>. This allows (1) creating data races to a `T: !Sync` and (2) sending `T: !Send` to other threads, resulting in memory corruption or other undefined behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36453
- https://github.com/rossdylan/rust-scottqueue/issues/1
- https://github.com/rossdylan/rust-scottqueue
- https://rustsec.org/advisories/RUSTSEC-2020-0133.html
