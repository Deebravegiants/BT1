# [C] Incorrect check on buffer length in rand_core

## Summary
Severity: Critical
Advisory: GHSA-w7j2-35mf-95p7
CVE: CVE-2021-27378
CWE: CWE-330
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w7j2-35mf-95p7
Type: github-advisory

## Affected
- crates.io: `rand_core` — affected >=0.6.0 <0.6.2

## Details
An issue was discovered in the rand_core crate before 0.6.2 for Rust. Because `read_u32_into` and `read_u64_into` mishandle certain buffer-length checks, a random number generator may be seeded with too little data. The vulnerability was introduced in v0.6.0. The advisory doesn't apply to earlier minor version numbers.

Because read_u32_into and read_u64_into mishandle certain buffer-length checks, a random number generator may be seeded with too little data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27378
- https://github.com/rust-random/rand/pull/1096
- https://github.com/rust-random/rand
- https://github.com/rust-random/rand/compare/0.6.0...rand_core-0.6.2#diff-f41b3dfa5ce28f3bee390d327c50621e141cf3569921f8e9ca15ccfcf25263a9R19
- https://github.com/rust-random/rand/compare/0.6.0...rand_core-0.6.2#diff-f41b3dfa5ce28f3bee390d327c50621e141cf3569921f8e9ca15ccfcf25263a9R28
- https://rustsec.org/advisories/RUSTSEC-2021-0023.html
