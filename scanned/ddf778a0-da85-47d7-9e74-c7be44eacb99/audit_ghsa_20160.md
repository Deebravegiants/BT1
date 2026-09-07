# [H] Window can read out of bounds if Read instance returns more bytes than buffer size

## Summary
Severity: High
Advisory: GHSA-q579-9wp9-gfp2
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-q579-9wp9-gfp2
Type: github-advisory

## Affected
- crates.io: `rdiff` — affected >=0

## Details
`rdiff` performs a diff of two provided strings or files. As part of its reading code it uses the return value of a `Read` instance to set the length of its internal character vector.

If the `Read` implementation claims that it has read more bytes than the length of the provided buffer, the length of the vector will be set to longer than its capacity. This causes `rdiff` APIs to return uninitialized memory in its API
methods.

## References
- https://github.com/dyule/rdiff/issues/3
- https://github.com/dyule/rdiff
- https://rustsec.org/advisories/RUSTSEC-2021-0094.html
