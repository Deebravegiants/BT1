# [H] InputStream::read_exact : `Read` on uninitialized buffer causes UB

## Summary
Severity: High
Advisory: GHSA-hmx9-jm3v-33hv
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-hmx9-jm3v-33hv
Type: github-advisory

## Affected
- crates.io: `buffoon` — affected >=0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` implementation.
Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer.
Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://github.com/carllerche/buffoon/issues/2
- https://github.com/carllerche/buffoon
- https://rustsec.org/advisories/RUSTSEC-2020-0154.html
