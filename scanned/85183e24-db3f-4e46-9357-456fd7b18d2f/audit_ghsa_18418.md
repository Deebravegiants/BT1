# [M] Rust Web Push is vulnerable to a DoS attack via a large integer in a Content-Length header

## Summary
Severity: Medium
Advisory: GHSA-287x-9rff-qvcg
CVE: CVE-2025-53604
CWE: CWE-130
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-05
Source: https://github.com/advisories/GHSA-287x-9rff-qvcg
Type: github-advisory

## Affected
- crates.io: `web-push` — affected >=0 <0.10.4

## Details
The web-push crate before 0.10.4 for Rust allows a denial of service (memory consumption) in the built-in clients via a large integer in a Content-Length header. The patch was initially made available in version 0.10.3, but version 0.10.3 has since been yanked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53604
- https://github.com/pimeys/rust-web-push/pull/68
- https://github.com/pimeys/rust-web-push/commit/8447ed86bf3f24629abd7022b94104bf3cd64453
- https://crates.io/crates/web-push
- https://github.com/pimeys/rust-web-push
- https://rustsec.org/advisories/RUSTSEC-2025-0015.html
