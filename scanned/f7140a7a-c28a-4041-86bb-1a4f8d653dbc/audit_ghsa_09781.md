# [M] pypdf has long runtimes for wrong size values in cross-reference and object streams

## Summary
Severity: Medium
Advisory: GHSA-jj6c-8h6c-hppx
CVE: CVE-2026-41168
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-jj6c-8h6c-hppx
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.10.1

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires cross-reference streams with wrong large `/Size` values or object streams with wrong large `/N` values.

### Patches

This has been fixed in [pypdf==6.10.1](https://github.com/py-pdf/pypdf/releases/tag/6.10.1).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3733](https://github.com/py-pdf/pypdf/pull/3733).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-jj6c-8h6c-hppx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41168
- https://github.com/py-pdf/pypdf/pull/3733
- https://github.com/py-pdf/pypdf/commit/62338e9d36419cf193ccec7331784f45df1d70b3
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.10.1
