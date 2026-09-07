# [H] webpki: CPU denial of service in certificate path building

## Summary
Severity: High
Advisory: GHSA-8qv2-5vq6-g2g7
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-8qv2-5vq6-g2g7
Type: github-advisory

## Affected
- crates.io: `webpki` — affected >=0 <0.22.2

## Details
When this crate is given a pathological certificate chain to validate, it will spend CPU time exponential with the number of candidate certificates at each step of path building.

Both TLS clients and TLS servers that accept client certificate are affected.

This was previously reported in https://github.com/briansmith/webpki/issues/69.

`rustls-webpki` is a fork of this crate which contains a fix for this issue and is actively maintained.

## References
- https://github.com/briansmith/webpki/issues/69
- https://github.com/briansmith/webpki/issues/69#issuecomment-1699894848
- https://github.com/briansmith/webpki/commit/30a108e0802fd09585e0d071013f24b8272d139b
- https://github.com/briansmith/webpki
- https://github.com/crypto-com/sgx-vendor
- https://rustsec.org/advisories/RUSTSEC-2023-0052.html
