# [M] pypdf: Possible infinite loop when processing threads/articles in writer

## Summary
Severity: Medium
Advisory: GHSA-g9xf-7f8q-9mcj
CVE: CVE-2026-54651
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-g9xf-7f8q-9mcj
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.13.1

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires merging a file with threads/articles into a writer.

### Patches

This has been fixed in [pypdf==6.13.1](https://github.com/py-pdf/pypdf/releases/tag/6.13.1).

### Workarounds

If users cannot upgrade yet, consider applying the changes from PR [#3839](https://github.com/py-pdf/pypdf/pull/3839).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-g9xf-7f8q-9mcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-54651
- https://github.com/py-pdf/pypdf/pull/3839
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.13.1
