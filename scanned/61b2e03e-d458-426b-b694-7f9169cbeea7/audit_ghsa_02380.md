# [M] Multiple memory safety issues in actix-web

## Summary
Severity: Medium
Advisory: GHSA-w65j-g6c7-g3m4
CWE: CWE-362
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w65j-g6c7-g3m4
Type: github-advisory

## Affected
- crates.io: `actix-web` — affected >=0 <0.7.19

## Details
Affected versions contain multiple memory safety issues, such as:

 - Unsoundly coercing immutable references to mutable references
 - Unsoundly extending lifetimes of strings
 - Adding the `Send` marker trait to objects that cannot be safely sent between threads

This may result in a variety of memory corruption scenarios, most likely use-after-free.
 
A signficant refactoring effort has been conducted to resolve these issues.

## References
- https://github.com/actix/actix-web/issues/289
- https://github.com/actix/actix-web
- https://rustsec.org/advisories/RUSTSEC-2018-0019.html
