# [M] mail-internals use-after-free vulnerability in `vec_insert_bytes`

## Summary
Severity: Medium
Advisory: GHSA-rcx8-48pc-v9q8
Ecosystem: crates.io
Published: 2023-08-24
Source: https://github.com/advisories/GHSA-rcx8-48pc-v9q8
Type: github-advisory

## Affected
- crates.io: `mail-internals` — affected >=0.2.0

## Details
Incorrect reallocation logic in the function [`vec_insert_bytes`](https://docs.rs/mail-internals/0.2.3/mail_internals/utils/fn.vec_insert_bytes.html) causes a use-after-free.

This function does not have to be called directly to trigger the vulnerability because many methods on [`EncodingWriter`](https://docs.rs/mail-internals/0.2.3/mail_internals/encoder/struct.EncodingWriter.html) call this function internally.

The mail-\* suite is unmaintained and the upstream sources have been actively vandalised.
A fixed `mail-internals-ng` (and `mail-headers-ng` and `mail-core-ng`) crate has been published which fixes this, and a dependency on another unsound crate.

## References
- https://github.com/rustsec/advisory-db/blob/main/crates/mail-internals/RUSTSEC-2023-0054.md
- https://rustsec.org/advisories/RUSTSEC-2023-0054.html
