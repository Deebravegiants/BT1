# [M] `openssl` `X509StoreRef::objects` is unsound

## Summary
Severity: Medium
Advisory: GHSA-xphf-cx8h-7q9g
Ecosystem: crates.io
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-xphf-cx8h-7q9g
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.29 <0.10.60

## Details
This function returned a reference into an OpenSSL datastructure, but there was no way to ensure OpenSSL would not mutate the datastructure behind one's back.

Use of this function should be replaced with `X509StoreRef::all_certificates`.

## References
- https://github.com/sfackler/rust-openssl/issues/2096
- https://github.com/sfackler/rust-openssl/commit/cf9681a55cabd4cb9f1475bde17b5079f2a0384e
- https://github.com/sfackler/rust-openssl
- https://rustsec.org/advisories/RUSTSEC-2023-0072.html
