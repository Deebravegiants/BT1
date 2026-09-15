# [H] LibYML: `libyml::string::yaml_string_extend` is unsound and unmaintained

## Summary
Severity: High
Advisory: GHSA-gfxp-f68g-8x78
CWE: CWE-758
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-gfxp-f68g-8x78
Type: github-advisory

## Affected
- crates.io: `libyml` — affected >=0.0.4

## Details
In version 0.0.4, `libyml::string::yaml_string_extend` was revised resulting in undefined behaviour, which is unsound.

The GitHub project for `libyml` was archived after unsoundness issues were raised.

If you rely on this crate, it is highly recommended switching to a maintained alternative.

## Recommended alternatives

- [`libyaml-safer`](https://crates.io/crates/libyaml-safer) 
- [`unsafe-libyaml-norway`](https://crates.io/crates/unsafe-libyaml-norway) - Maintained fork of `unsafe-libyaml`

## References
- https://github.com/rustsec/advisory-db/issues/2395
- https://github.com/sebastienrousseau/libyml
- https://rustsec.org/advisories/RUSTSEC-2025-0067.html
