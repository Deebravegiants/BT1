# [H] olm-sys: wrapped library unmaintained, potentially vulnerable

## Summary
Severity: High
Advisory: GHSA-p2q9-36vw-c468
CWE: CWE-1395
Ecosystem: crates.io
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-p2q9-36vw-c468
Type: github-advisory

## Affected
- crates.io: `olm-sys` — affected >=0

## Details
After several cryptographic vulnerabilities in `libolm` were disclosed publicly, the Matrix Foundation has [officially deprecated the library](https://matrix.org/blog/2024/08/libolm-deprecation/). `olm-sys` is a thin wrapper around `libolm` and is now deprecated and potentially vulnerable in kind.

Users of `olm-sys` and its higher-level abstraction, `olm-rs`, are highly encouraged to switch to [`vodozemac`](https://crates.io/crates/vodozemac) as soon as possible. It is the successor effort to `libolm` and is written in Rust.

## References
- https://gitlab.gnome.org/BrainBlasted/olm-sys
- https://gitlab.gnome.org/BrainBlasted/olm-sys/-/issues/12
- https://matrix.org/blog/2024/08/libolm-deprecation
- https://rustsec.org/advisories/RUSTSEC-2024-0368.html
