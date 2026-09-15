# [H] Deserialization functions pass uninitialized memory to user-provided Read

## Summary
Severity: High
Advisory: GHSA-m325-rxjv-pwph
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-m325-rxjv-pwph
Type: github-advisory

## Affected
- crates.io: `messagepack-rs` — affected >=0

## Details
Affected versions of this crate passed an uninitialized buffer to a
user-provided `Read` instance in:

* `deserialize_binary`
* `deserialize_string`
* `deserialize_extension_others`
* `deserialize_string_primitive`

This can result in safe `Read` implementations reading from the uninitialized
buffer leading to undefined behavior.

## References
- https://github.com/otake84/messagepack-rs/issues/2
- https://github.com/otake84/messagepack-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0092.html
