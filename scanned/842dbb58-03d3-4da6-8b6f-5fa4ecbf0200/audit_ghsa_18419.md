# [M] Matrix Rust SDK vulnerable to SQL Injection through its EventCache implementation

## Summary
Severity: Medium
Advisory: GHSA-275g-g844-73jh
CVE: CVE-2025-53549
CWE: CWE-89
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-275g-g844-73jh
Type: github-advisory

## Affected
- crates.io: `matrix-sdk` — affected >=0.11.0 <0.13.0
- crates.io: `matrix-sdk-sqlite` — affected >=0.11.0 <0.13.0

## Details
An SQL injection vulnerability in the `EventCache::find_event_with_relations` method of matrix-sdk 0.11 and 0.12 allows malicious room members to execute arbitrary SQL commands in Matrix clients that directly pass relation types provided by those room members into this method, when used with the default sqlite-based store backend. Exploitation is unlikely, as no known clients currently use the API in this manner.

### Workarounds

Passing only trusted (or sanitised) relation types to the `filter` argument of `EventCache::find_event_with_relations()` avoids the issue.

### Patches

The issue is fixed in matrix-sdk 0.13.

### References

The issue was introduced in https://github.com/matrix-org/matrix-rust-sdk/pull/4849.

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-275g-g844-73jh
- https://nvd.nist.gov/vuln/detail/CVE-2025-53549
- https://github.com/matrix-org/matrix-rust-sdk/pull/4849
- https://github.com/matrix-org/matrix-rust-sdk/commit/d0c01006e4808db5eb96ad5c496416f284d8bd3c
- https://github.com/matrix-org/matrix-rust-sdk
- https://rustsec.org/advisories/RUSTSEC-2025-0043.html
