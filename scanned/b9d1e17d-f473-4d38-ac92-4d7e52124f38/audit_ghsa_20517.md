# [C] Incorrect hash in sha2

## Summary
Severity: Critical
Advisory: GHSA-fc7x-2cmc-8j2g
CVE: CVE-2021-45696
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-fc7x-2cmc-8j2g
Type: github-advisory

## Affected
- crates.io: `sha2` — affected >=0.9.7 <0.9.8

## Details
The v0.9.7 release of the sha2 crate introduced a new AVX2-accelerated backend which was automatically enabled for all x86/x86_64 CPUs where AVX2 support was autodetected at runtime.

This backend was buggy and would miscompute results for long messages (i.e. messages spanning multiple SHA blocks).

The crate has since been yanked, but any users who upgraded to v0.9.7 should immediately upgrade to v0.9.8 and recompute any hashes which were previously computed by v0.9.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45696
- https://github.com/RustCrypto/hashes/pull/314
- https://github.com/RustCrypto/hashes
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/sha2/RUSTSEC-2021-0100.md
- https://rustsec.org/advisories/RUSTSEC-2021-0100.html
