# [M] Library exclusively intended to obfuscate code.

## Summary
Severity: Medium
Advisory: GHSA-gfg9-x6px-r7gr
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-gfg9-x6px-r7gr
Type: github-advisory

## Affected
- crates.io: `plutonium` — affected >=0

## Details
This crate allows you to write safe functions with unsafe bodies without the `unsafe` keyword.

The value this adds is questionable, and hides `unsafe` usages from naive analysis.

## References
- https://github.com/mxxo/plutonium
- https://rustsec.org/advisories/RUSTSEC-2020-0011.html
