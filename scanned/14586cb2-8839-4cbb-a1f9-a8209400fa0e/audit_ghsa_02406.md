# [H] fake-static allows converting any reference into a `'static` reference

## Summary
Severity: High
Advisory: GHSA-8xw8-mmqv-frqq
CWE: CWE-657
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8xw8-mmqv-frqq
Type: github-advisory

## Affected
- crates.io: `fake-static` — affected >=0

## Details
fake-static allows converting a reference with any lifetime into
a reference with `'static` lifetime without the `unsafe` keyword.

Internally, this crate does not use unsafe code, it instead
exploits a soundness bug in rustc

## References
- https://github.com/rust-lang/rust/issues/25860
- https://github.com/NieDzejkob/fake-static
- https://rustsec.org/advisories/RUSTSEC-2020-0013.html
