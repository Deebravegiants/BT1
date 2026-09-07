# [M] webp crate may expose memory contents when encoding an image

## Summary
Severity: Medium
Advisory: GHSA-9q78-27f3-2jmh
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-9q78-27f3-2jmh
Type: github-advisory

## Affected
- crates.io: `webp` — affected >=0 <0.3.1

## Details
Affected versions of this crate did not check that the input slice passed to `"webp::Encoder::encode()` is large enough for the specified image dimensions.

If the input slice is too short, the library will read out of bounds of the buffer and encode other memory contents as an image, resulting in memory exposure or a segmentation fault.

The flaw was corrected in [pull request #44](https://github.com/jaredforth/webp/pull/44) by always validating the input buffer size when constructing the encoder.

## References
- https://github.com/jaredforth/webp/issues/40
- https://github.com/jaredforth/webp/pull/44
- https://github.com/jaredforth/webp/commit/62b47060d7fb8cc0e92e522ee54948edf5aab556
- https://github.com/jaredforth/webp
- https://rustsec.org/advisories/RUSTSEC-2024-0443.html
