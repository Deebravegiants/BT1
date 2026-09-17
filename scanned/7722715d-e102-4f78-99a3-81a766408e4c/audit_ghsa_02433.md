# [H] Data races in slock

## Summary
Severity: High
Advisory: GHSA-mc36-5m36-hjh5
CVE: CVE-2020-36455
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mc36-5m36-hjh5
Type: github-advisory

## Affected
- crates.io: `slock` — affected >=0 <0.2.0

## Details
An issue was discovered in the slock crate through 2020-11-17 for Rust. Slock<T> unconditionally implements Send and Sync.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36455
- https://github.com/BrokenLamp/slock-rs/issues/2
- https://github.com/BrokenLamp/slock-rs/commit/719df35f55b6cab4ca2a7f840347a06ecbd8aac6
- https://github.com/BrokenLamp/slock-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/slock/RUSTSEC-2020-0135.md
- https://rustsec.org/advisories/RUSTSEC-2020-0135.html
