# [M] pypdf: Possible infinite loop during recovery attempts in DictionaryObject.read_from_stream

## Summary
Severity: Medium
Advisory: GHSA-87mj-5ggw-8qc3
CVE: CVE-2026-33699
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-87mj-5ggw-8qc3
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.9.2

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires reading a file in non-strict mode.

### Patches

This has been fixed in [pypdf==6.9.2](https://github.com/py-pdf/pypdf/releases/tag/6.9.2).

### Workarounds

If users cannot upgrade yet, consider applying the changes from PR [#3693](https://github.com/py-pdf/pypdf/pull/3693).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-87mj-5ggw-8qc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33699
- https://github.com/py-pdf/pypdf/pull/3693
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.9.2
