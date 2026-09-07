# [M] pypdf: Inefficient handling of non-whitespace inputs in read_until_whitespace

## Summary
Severity: Medium
Advisory: GHSA-fc8x-2rww-xw9m
CVE: CVE-2026-82398
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-fc8x-2rww-xw9m
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.15.0

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires a call to `read_until_whitespace` with an input which does not have whitespace for a long time.

### Patches
This has been fixed in [pypdf==6.15.0](https://github.com/py-pdf/pypdf/releases/tag/6.15.0).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3947](https://github.com/py-pdf/pypdf/pull/3947).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-fc8x-2rww-xw9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-82398
- https://github.com/py-pdf/pypdf/pull/3947
- https://github.com/py-pdf/pypdf/commit/4959848e057e37c218dccad7465259210923faaa
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.15.0
