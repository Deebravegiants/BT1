# [M] Space bug in `clean_text`

## Summary
Severity: Medium
Advisory: GHSA-p2g9-94wh-65c2
CWE: CWE-79
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-p2g9-94wh-65c2
Type: github-advisory

## Affected
- crates.io: `ammonia` — affected >=3.0.0 <3.1.3

## Details
An incorrect mapping from HTML specification to ASCII codes was used.
Because HTML treats the Form Feed as whitespace, code like this has an injection bug:

    let html = format!("<div title={}>", clean_text(user_supplied_string));

Applications are not affected if they quote their attributes, or if they don't use `clean_text` at all.

## References
- https://github.com/rust-ammonia/ammonia/pull/147
- https://github.com/rust-ammonia/ammonia/commit/6c7bf22907a75d1bbaed52e4f7dd9716f5e6f737
- https://github.com/rust-ammonia/ammonia
- https://rustsec.org/advisories/RUSTSEC-2022-0003.html
