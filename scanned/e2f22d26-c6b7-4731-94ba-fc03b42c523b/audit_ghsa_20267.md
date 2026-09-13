# [H] Parser creates invalid uninitialized value

## Summary
Severity: High
Advisory: GHSA-f67m-9j94-qv9j
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-f67m-9j94-qv9j
Type: github-advisory

## Affected
- crates.io: `hyper` — affected >=0 <0.14.12

## Details
Affected versions of this crate called `mem::uninitialized()` in the HTTP1 parser to create values of type `httparse::Header` (from the `httparse` crate).
This is unsound, since `Header` contains references and thus must be non-null.
 
The flaw was corrected by avoiding the use of `mem::uninitialized()`, using `MaybeUninit` instead.

## References
- https://github.com/hyperium/hyper/pull/2545
- https://github.com/hyperium/hyper
- https://rustsec.org/advisories/RUSTSEC-2022-0022.html
