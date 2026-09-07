# [M] Vditor allows Cross-site Scripting via an attribute of an `A` element

## Summary
Severity: Medium
Advisory: GHSA-m5jf-8crm-r65m
CVE: CVE-2024-34449
CWE: CWE-79
Ecosystem: npm
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-m5jf-8crm-r65m
Type: github-advisory

## Affected
- npm: `vditor` — affected 3.10.3

## Details
Vditor 3.10.3 allows XSS via an attribute of an `A` element.

NOTE: the vendor indicates that a user is supposed to mitigate this via `sanitize=true`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34449
- https://github.com/Vanessa219/vditor/issues/1604
- https://github.com/Vanessa219/vditor
- https://github.com/Vanessa219/vditor/blob/b3a14d6e4462b0c17141e1fcc66173264ada64e0/README_en_US.md?plain=1#L310
