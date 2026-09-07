# [M] Unsoundness in anstream

## Summary
Severity: Medium
Advisory: GHSA-2rxc-gjrp-vjhx
Ecosystem: crates.io
Published: 2024-12-04
Source: https://github.com/advisories/GHSA-2rxc-gjrp-vjhx
Type: github-advisory

## Affected
- crates.io: `anstream` — affected >=0 <0.6.8

## Details
When given a valid UTF8 string "ö\x1b😀", the function in crates/anstream/src/adapter/strip.rs will be confused. The UTF8 bytes are \xc3\xb6 then \x1b then \xf0\x9f\x98\x80.

When looping over "non-printable bytes" \x1b\xf0 will be considered as some non-printable sequence.

This will produce a broken str from the incorrectly segmented bytes via str::from_utf8_unchecked, and that should never happen.

Full credit goes to @Ralith who reviewed this code and asked @burakemir to follow up.

## References
- https://github.com/rust-cli/anstyle/issues/156
- https://github.com/rust-cli/anstyle
- https://rustsec.org/advisories/RUSTSEC-2024-0404.html
