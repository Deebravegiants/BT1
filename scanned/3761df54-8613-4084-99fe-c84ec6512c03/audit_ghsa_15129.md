# [M] html injection vulnerability in the `tuitse_html` function.

## Summary
Severity: Medium
Advisory: GHSA-m4m5-j36m-8x72
CVE: CVE-2024-23341
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-m4m5-j36m-8x72
Type: github-advisory

## Affected
- PyPI: `TuiTse-TsuSin` — affected >=0 <1.3.2

## Details
### Impact

When using `tuitse_html` without quoting the input, there is a html injection vulnerability. It should use the django version `django.utils.html.format_html`, instead of `string.format()`

### Patches

Upgrade to version 1.3.2.

### Workarounds


Sanitizing Taigi input with HTML quotation.

### References


https://github.com/i3thuan5/TuiTse-TsuSin/pull/22

## References
- https://github.com/i3thuan5/TuiTse-TsuSin/security/advisories/GHSA-m4m5-j36m-8x72
- https://nvd.nist.gov/vuln/detail/CVE-2024-23341
- https://github.com/i3thuan5/TuiTse-TsuSin/pull/22
- https://github.com/i3thuan5/TuiTse-TsuSin/commit/9d21d99d7cfcd7c42aade251fab98ec102e730ea
- https://github.com/i3thuan5/TuiTse-TsuSin
- https://github.com/pypa/advisory-database/tree/main/vulns/tuitse-tsusin/PYSEC-2024-22.yaml
