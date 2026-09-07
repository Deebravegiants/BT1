# [H] Data race in tiny_future

## Summary
Severity: High
Advisory: GHSA-fg42-vwxx-xx5j
CVE: CVE-2020-36438
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fg42-vwxx-xx5j
Type: github-advisory

## Affected
- crates.io: `tiny_future` — affected >=0 <0.4.0

## Details
tiny_future contains a light-weight implementation of Futures. The Future type it has lacked bound on its Send and Sync traits. This allows for a bug where non-thread safe types such as Cell can be used in Futures and cause data races in concurrent programs. The flaw was corrected in commit `c791919` by adding trait bounds to Future's Send and Sync.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36438
- https://github.com/KizzyCode/tiny_future/issues/1
- https://github.com/KizzyCode/tiny_future-rust/commit/c7919199a0f6d1ce0e3c33499d1b37f862c990e4
- https://github.com/KizzyCode/tiny_future
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/tiny_future/RUSTSEC-2020-0118.md
- https://rustsec.org/advisories/RUSTSEC-2020-0118.html
