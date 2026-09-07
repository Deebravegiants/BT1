# [M] Unchecked vector pre-allocation

## Summary
Severity: Medium
Advisory: GHSA-mcrf-7hf9-f6q5
CWE: CWE-400
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mcrf-7hf9-f6q5
Type: github-advisory

## Affected
- crates.io: `rmpv` — affected >=0 <0.4.2

## Details
Affected versions of this crate pre-allocate memory on deserializing raw buffers without checking whether there is sufficient data available. This allows an attacker to do denial-of-service attacks by sending small msgpack messages that allocate gigabytes of memory.

## References
- https://github.com/3Hren/msgpack-rust/issues/151
- https://github.com/3Hren/msgpack-rust
- https://rustsec.org/advisories/RUSTSEC-2017-0006.html
