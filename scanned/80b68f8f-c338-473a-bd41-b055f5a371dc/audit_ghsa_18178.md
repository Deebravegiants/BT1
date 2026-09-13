# [M] serde_yml crate is unsound and unmaintained

## Summary
Severity: Medium
Advisory: GHSA-hhw4-xg65-fp2x
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-hhw4-xg65-fp2x
Type: github-advisory

## Affected
- crates.io: `serde_yml` — affected >=0

## Details
Using `serde_yml::ser::Serializer.emitter` can cause a segmentation fault, which is unsound.

The GitHub project for `serde_yml` was archived after unsoundness issues were raised.

If you rely on this crate, it is highly recommended switching to a maintained alternative.

## Recommended alternatives

- [`serde_norway`](https://crates.io/crates/serde_norway) - Maintained fork of `serde_yaml`, using `unsafe-libyaml-norway`
- [`serde_yaml_ng`](https://crates.io/crates/serde_yaml_ng) - Maintained fork of `serde_yaml`, using unmaintained `unsafe-libyaml`

## Incomplete pure Rust alternatives

These implementation do not rely on C `libyaml`.

- [`serde_yaml2`](https://crates.io/crates/serde_yaml2)
- [`yaml-peg`](https://crates.io/crates/yaml-peg)

## References
- https://github.com/rustsec/advisory-db/issues/2395
- https://github.com/sebastienrousseau/serde_yml
- https://rustsec.org/advisories/RUSTSEC-2025-0068.html
