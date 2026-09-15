# [H] mozjpeg DecompressScanlines::read_scanlines is Unsound

## Summary
Severity: High
Advisory: GHSA-v8gq-5grq-9728
Ecosystem: crates.io
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-v8gq-5grq-9728
Type: github-advisory

## Affected
- crates.io: `mozjpeg` — affected >=0 <0.8.19

## Details
This issue and vector is similar to [RUSTSEC-2020-0029] of `rgb` crate which `mozjpeg` depends on.

Affected versions of `mozjpeg` crate allow creating instances of any type `T` from bytes,
and do not correctly constrain `T` to the types for which it is safe to do so.

Examples of safety violation possible for a type `T`:

* `T` contains a reference type, and it constructs a pointer to an invalid, arbitrary memory address.
* `T` requires a safety and/or validity invariant for its construction that may be violated.

The issue was fixed in 0.8.19 by using safer types and involving `rgb` dependency bump.

[RUSTSEC-2020-0029]: https://rustsec.org/advisories/RUSTSEC-2020-0029.html

## References
- https://github.com/ImageOptim/mozjpeg-rust/issues/10
- https://github.com/ImageOptim/mozjpeg-rust
- https://rustsec.org/advisories/RUSTSEC-2020-0165.html
