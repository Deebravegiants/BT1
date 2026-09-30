# [M] Data races in im

## Summary
Severity: Medium
Advisory: GHSA-q9h2-4xhf-23xx
CVE: CVE-2020-36204
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-q9h2-4xhf-23xx
Type: github-advisory

## Affected
- crates.io: `im` — affected >=12.0.0 <15.1.0

## Details
An issue was discovered in the im crate prior to 15.1.0 for Rust. Because TreeFocus does not have bounds on its Send trait or Sync trait, a data race can occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36204
- https://github.com/bodil/im-rs/issues/157
- https://github.com/bodil/im-rs/pull/158
- https://github.com/bodil/im-rs/commit/0b3a7b228b0fe70446393f55c8b893f349f3f6bd
- https://github.com/bodil/im-rs
- https://github.com/bodil/im-rs/releases/tag/v15.1.0
- https://rustsec.org/advisories/RUSTSEC-2020-0096.html
