# [M] Improper random number generation in nanorand

## Summary
Severity: Medium
Advisory: GHSA-m9m5-cg5h-r582
CVE: CVE-2020-35926
CWE: CWE-338
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m9m5-cg5h-r582
Type: github-advisory

## Affected
- crates.io: `nanorand` — affected >=0 <0.5.1

## Details
In versions of nanorand prior to 0.5.1, RandomGen implementations for standard unsigned integers could fail to properly generate numbers, due to using bit-shifting to truncate a 64-bit number, rather than just an as conversion. This often manifested as RNGs returning nothing but 0, including the cryptographically secure ChaCha random number generator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35926
- https://github.com/Absolucy/nanorand-rs/commit/5ba218ac29df4786b002d7d12b47fa0c04a331f2
- https://github.com/Absolucy/nanorand-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0089.html
- https://twitter.com/aspenluxxxy/status/1336684692284772352
