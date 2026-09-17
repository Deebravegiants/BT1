# [H] Non-aligned u32 read in Chacha20 encryption and decryption

## Summary
Severity: High
Advisory: GHSA-pmcv-mgcf-rvxg
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-pmcv-mgcf-rvxg
Type: github-advisory

## Affected
- crates.io: `crypto2` — affected >=0

## Details
The implementation does not enforce alignment requirements on input slices while incorrectly assuming 4-byte alignment through an unsafe call to `std::slice::from_raw_parts_mut`, which breaks the contract and introduces undefined behavior.

This affects Chacha20 encryption and decryption in crypto2.

## References
- https://github.com/shadowsocks/crypto2/issues/27
- https://github.com/shadowsocks/crypto2
- https://rustsec.org/advisories/RUSTSEC-2021-0121.html
