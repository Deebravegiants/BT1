# [M] pypdf: Possible long runtimes/large memory usage when extracting XForm objects

## Summary
Severity: Medium
Advisory: GHSA-763m-79hh-57f2
CVE: CVE-2026-84311
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-763m-79hh-57f2
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.16.1

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to long runtimes and large memory consumption. This requires extracting the text of a page with lots of XForm objects, where some of them might be re-used.

### Patches

This has been fixed in [pypdf==6.16.1](https://github.com/py-pdf/pypdf/releases/tag/6.16.1).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3966](https://github.com/py-pdf/pypdf/pull/3966).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-763m-79hh-57f2
- https://github.com/py-pdf/pypdf/pull/3966
- https://github.com/py-pdf/pypdf/commit/d91ab705fd81ed1a9cec175c6958600dea1a4942
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.16.1
