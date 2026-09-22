# [M] Improper synchronization in buttplug

## Summary
Severity: Medium
Advisory: GHSA-r7rv-2rph-hvhj
CVE: CVE-2020-36218
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r7rv-2rph-hvhj
Type: github-advisory

## Affected
- crates.io: `buttplug` — affected >=0 <1.0.4

## Details
An issue was discovered in the buttplug crate before 1.0.4 for Rust. ButtplugFutureStateShared does not properly consider (!Send|!Sync) objects, leading to a data race.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36218
- https://github.com/buttplugio/buttplug-rs/issues/225
- https://github.com/buttplugio/buttplug-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0112.html
