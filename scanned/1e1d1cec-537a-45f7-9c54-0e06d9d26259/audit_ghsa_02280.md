# [C] Incorrect Comparison in sodiumoxide

## Summary
Severity: Critical
Advisory: GHSA-wrvc-72w7-xpmj
CVE: CVE-2019-25002
CWE: CWE-697
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wrvc-72w7-xpmj
Type: github-advisory

## Affected
- crates.io: `sodiumoxide` — affected >=0.2.0 <0.2.5

## Details
An issue was discovered in the sodiumoxide crate starting with 0.2.0 and prior to 0.2.5 for Rust. `generichash::Digest::eq` compares itself to itself and thus has degenerate security properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25002
- https://github.com/sodiumoxide/sodiumoxide/pull/381
- https://github.com/sodiumoxide/sodiumoxide/pull/381/commits/fae052b834b097ced9a89a8fff8466e18f383070
- https://github.com/sodiumoxide/sodiumoxide/commit/38490723927f230498adf795153e6cd3cb08b6a8
- https://github.com/sodiumoxide/sodiumoxide
- https://rustsec.org/advisories/RUSTSEC-2019-0026.html
