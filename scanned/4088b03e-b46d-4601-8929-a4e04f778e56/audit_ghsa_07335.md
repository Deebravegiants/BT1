# [H] Thumbor has Regex Denial of Service (ReDoS) in `convolution` filter

## Summary
Severity: High
Advisory: GHSA-5vjc-7cxw-4w6j
CVE: CVE-2026-53504
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-5vjc-7cxw-4w6j
Type: github-advisory

## Affected
- PyPI: `thumbor` — affected >=0 <7.8.0

## Details
### Summary
The regular expression used to parse the `convolution` filter exhibits exponential-time backtracking for certain inputs, enabling a Regular Expression Denial of Service (ReDoS).

### Details
The RegExp for `convolution` is defined as `convolution\((?:\s*((?:[-]?[\d]+\.?[\d]*[;])*(?:[-]?[\d]+\.?[\d]*))\s*)(?:,\s*([\d]+)\s*)(?:,\s*([Tt]rue|[Ff]alse|1|0)\s*)?\)`. Within this expression a dangerous subpattern effectively behaves like `(\d+)*,\d+`.

### PoC
A filter string containing many repeated values will exhaust `re.match`:
- `convolution(-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11)`
- http://localhost:8888/unsafe/0x0/smart/filters:convolution(-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11;-11)/x.png

The evaluation occurs on https://github.com/thumbor/thumbor/blob/master/thumbor/filters/__init__.py#L189.

### Impact
A specially crafted URL will lead to denial of service, as new images won't be processed until `re.match` returns.

## References
- https://github.com/thumbor/thumbor/security/advisories/GHSA-5vjc-7cxw-4w6j
- https://github.com/thumbor/thumbor/commit/3f38fe1610d20168e91f76d432212de30727eb2e
- https://github.com/thumbor/thumbor
- https://github.com/thumbor/thumbor/releases/tag/7.8.0
