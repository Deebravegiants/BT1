# [H] CVE-2021-34121

## Summary
Severity: High
Advisory: CVE-2021-34121
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2021-34121
Type: osv

## Details
An Out of Bounds flaw was discovered in htmodoc 1.9.12 in function parse_tree() in toc.cxx, this possibly leads to memory layout information leaking in the data. This might be used in a chain of vulnerability in order to reach code execution.

## References
- https://github.com/michaelrsweet/htmldoc/issues/433
- https://github.com/michaelrsweet/htmldoc/commit/c67bbd8756f015e33e4ba639a40c7f9d8bd9e8ab
