# [M] Uncontrolled recursion leads to abort in deserialization

## Summary
Severity: Medium
Advisory: GHSA-39vw-qp34-rmwf
CWE: CWE-674
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-39vw-qp34-rmwf
Type: github-advisory

## Affected
- crates.io: `serde_yaml` — affected >=0.6.0-rc1 <0.8.4

## Details
Affected versions of this crate did not properly check for recursion while deserializing aliases. This allows an attacker to make a YAML file with an alias referring to itself causing an abort. The flaw was corrected by checking the recursion depth.

## References
- https://github.com/dtolnay/serde-yaml/pull/105
- https://github.com/dtolnay/serde-yaml/commit/b93aff6e904cffbbfd1f421b82f6dcc5ca19a4fd
- https://github.com/dtolnay/serde-yaml
- https://rustsec.org/advisories/RUSTSEC-2018-0005.html
