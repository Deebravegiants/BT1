# [H] `Read` on uninitialized buffer in `fill_buf()` and `read_up_to()`

## Summary
Severity: High
Advisory: GHSA-hv9v-7w3v-rj6f
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-hv9v-7w3v-rj6f
Type: github-advisory

## Affected
- crates.io: `acc_reader` — affected >=0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` implementation.

Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer.

Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://github.com/netvl/acc_reader/issues/1
- https://github.com/netvl/acc_reader
- https://rustsec.org/advisories/RUSTSEC-2020-0155.html
