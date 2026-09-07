# [M] pypdf: Possible long runtimes for zero-only width values in cross-reference streamsuntimes for zero-only width values in cross-reference streams

## Summary
Severity: Medium
Advisory: GHSA-248m-82v9-q6g6
CVE: CVE-2026-48156
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-248m-82v9-q6g6
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.12.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires cross-reference streams with `/W [0 0 0]` values and large `/Size` values.

### Patches

This has been fixed in [pypdf==6.12.0](https://github.com/py-pdf/pypdf/releases/tag/6.12.0).

### Workarounds

If developers are unable to upgrade their apps immediately, they should consider applying the changes from PR [#3791](https://github.com/py-pdf/pypdf/pull/3791).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-248m-82v9-q6g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48156
- https://github.com/py-pdf/pypdf/pull/3791
- https://github.com/py-pdf/pypdf/commit/507d7c9aa6ea83389b954b9c3c0c528fe5d5da70
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.12.0
