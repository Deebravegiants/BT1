# [C] Free of uninitialized memory in telemetry

## Summary
Severity: Critical
Advisory: GHSA-hpcx-3pw8-g3j2
CVE: CVE-2021-29937
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hpcx-3pw8-g3j2
Type: github-advisory

## Affected
- crates.io: `telemetry` — affected >=0 <0.1.3

## Details
An issue was discovered in the telemetry crate through 0.1.2 for Rust. There is a drop of uninitialized memory if a value.clone() call panics within misc::vec_with_size()

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29937
- https://github.com/Yoric/telemetry.rs/issues/45
- https://github.com/Yoric/telemetry.rs/commit/2820cf12f2e08645fd6d1f15b4a90a54d6082a81
- https://github.com/Yoric/telemetry.rs
- https://rustsec.org/advisories/RUSTSEC-2021-0046.html
