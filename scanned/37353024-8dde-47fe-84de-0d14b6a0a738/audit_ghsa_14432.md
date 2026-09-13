# [H] `openssl` `SubjectAlternativeName` and `ExtendedKeyUsage::other` allow arbitrary file read

## Summary
Severity: High
Advisory: GHSA-9qwg-crg9-m2vc
Ecosystem: crates.io
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-9qwg-crg9-m2vc
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.9.7 <0.10.48

## Details
`SubjectAlternativeName` and `ExtendedKeyUsage` arguments were parsed using the OpenSSL function `X509V3_EXT_nconf`. This function parses all input using an OpenSSL mini-language which can perform arbitrary file reads.

Thanks to David Benjamin (Google) for reporting this issue.

## References
- https://github.com/sfackler/rust-openssl/pull/1854
- https://github.com/sfackler/rust-openssl
- https://rustsec.org/advisories/RUSTSEC-2023-0023.html
