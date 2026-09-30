# [H] `openssl` `X509Extension::new` and `X509Extension::new_nid` null pointer dereference

## Summary
Severity: High
Advisory: GHSA-6hcf-g6gr-hhcr
CWE: CWE-476
Ecosystem: crates.io
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-6hcf-g6gr-hhcr
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.9.7 <0.10.48

## Details
These functions would crash when the context argument was None with certain extension types.

Thanks to David Benjamin (Google) for reporting this issue.

## References
- https://github.com/sfackler/rust-openssl/pull/1854
- https://github.com/sfackler/rust-openssl
- https://rustsec.org/advisories/RUSTSEC-2023-0024.html
