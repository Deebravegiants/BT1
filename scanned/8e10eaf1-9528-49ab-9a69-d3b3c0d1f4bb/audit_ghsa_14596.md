# [M] NULL pointer derefernce in `stb_image`

## Summary
Severity: Medium
Advisory: GHSA-ppjr-267j-5p9x
CWE: CWE-476
Ecosystem: crates.io
Published: 2023-03-20
Source: https://github.com/advisories/GHSA-ppjr-267j-5p9x
Type: github-advisory

## Affected
- crates.io: `stb_image` — affected >=0 <0.2.5

## Details
A bug in error handling in the `stb_image` C library could cause a NULL pointer dereference when attempting to load an invalid or unsupported image file.  This is fixed in version 0.2.5 and later of the `stb_image` Rust crate, by patching the C code to correctly handle NULL pointers.

## References
- https://github.com/servo/rust-stb-image/pull/102
- https://github.com/servo/rust-stb-imag
- https://rustsec.org/advisories/RUSTSEC-2023-0021.html
