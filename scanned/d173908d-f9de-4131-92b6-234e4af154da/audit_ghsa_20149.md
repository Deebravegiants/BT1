# [H] `Read` on uninitialized buffer may cause UB ( `read_entry()` )

## Summary
Severity: High
Advisory: GHSA-p56p-gq3f-whg8
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-p56p-gq3f-whg8
Type: github-advisory

## Affected
- crates.io: `flumedb` — affected >=0 <0.1.6

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided `Read` implementation.
There are two of such cases (`go_offset_log::read_entry()` & `offset_log::read_entry()`).

Arbitrary `Read` implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer.
Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://github.com/sunrise-choir/flumedb-rs/issues/10
- https://github.com/sunrise-choir/flumedb-rs/pull/12/commits/1b643df85ca4a56f7d96105a9eb35e1b917ee488
- https://github.com/sunrise-choir/flumedb-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0086.html
