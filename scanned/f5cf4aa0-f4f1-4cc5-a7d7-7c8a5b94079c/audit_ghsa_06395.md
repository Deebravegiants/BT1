# [M] pypdf: Possible infinite loop for TreeObject.insert_child

## Summary
Severity: Medium
Advisory: GHSA-jp53-mhqp-8xcg
CVE: CVE-2026-84309
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-jp53-mhqp-8xcg
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.16.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires a (usually writing) code path where `TreeObject.insert_child` is involved.

### Patches

This has been fixed in [pypdf==6.16.0](https://github.com/py-pdf/pypdf/releases/tag/6.16.0).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3964](https://github.com/py-pdf/pypdf/pull/3964).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-jp53-mhqp-8xcg
- https://github.com/py-pdf/pypdf/pull/3964
- https://github.com/py-pdf/pypdf/commit/c9ba557d565d57c53a0b3a0be06c0a4c29b0559b
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.16.0
