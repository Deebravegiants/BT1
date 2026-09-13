# [M] Improper `Sync` implementation on `FuturesUnordered` in futures-utils can cause data corruption

## Summary
Severity: Medium
Advisory: GHSA-5r9g-j7jj-hw6c
CVE: CVE-2020-35908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5r9g-j7jj-hw6c
Type: github-advisory

## Affected
- crates.io: `futures-util` — affected >=0.3.0 <0.3.2

## Details
An issue was discovered in the futures-util crate before 0.3.2 for Rust. FuturesUnordered can lead to data corruption because Sync is mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35908
- https://github.com/rust-lang/futures-rs/issues/2050
- https://github.com/rust-lang/futures-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0062.html
