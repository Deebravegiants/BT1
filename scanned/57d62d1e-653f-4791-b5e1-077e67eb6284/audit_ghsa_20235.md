# [M] `array!` macro is unsound when its length is impure constant

## Summary
Severity: Medium
Advisory: GHSA-7v4j-8wvr-v55r
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-7v4j-8wvr-v55r
Type: github-advisory

## Affected
- crates.io: `array-macro` — affected >=2.1.0 <2.1.2

## Details
Affected versions of this crate did substitute the array length provided by an user at compile-time multiple times.

When an impure constant expression is passed as an array length (such as a result of an impure procedural macro), this can result in the initialization of an array with uninitialized types, which in turn can allow an attacker to execute arbitrary code.

The flaw was corrected in commit [d5b63f72](https://github.com/xfix/array-macro/commit/d5b63f72090f3809c21ac28f9cfd84f12559bf7d) by making sure that array length is substituted just once.

## References
- https://github.com/xfix/array-macro/commit/d5b63f72090f3809c21ac28f9cfd84f12559bf7d
- https://github.com/rustsec/advisory-db/blob/main/crates/array-macro/RUSTSEC-2022-0017.md
- https://github.com/xfix/array-macro
- https://gitlab.com/KonradBorowski/array-macro/-/issues/5
- https://rustsec.org/advisories/RUSTSEC-2022-0017.html
