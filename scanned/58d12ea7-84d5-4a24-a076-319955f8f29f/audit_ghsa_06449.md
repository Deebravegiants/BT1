# [H] pypdf: Possible infinite loop for not terminated inline images (ASCII85 and ASCIIHex filter)

## Summary
Severity: High
Advisory: GHSA-g867-7843-wf8q
CVE: CVE-2026-59935
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-g867-7843-wf8q
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.14.2

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires parsing the content stream of a page with a not terminated inline image, as done when extracting the page text for example. It only affects the ASCII85 and ASCIIHex filters.

### Patches

This has been fixed in [pypdf==6.14.2](https://github.com/py-pdf/pypdf/releases/tag/6.14.2).

### Workarounds

If you cannot upgrade yet, consider applying the changes from PR [#3892](https://github.com/py-pdf/pypdf/pull/3892).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-g867-7843-wf8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-59935
- https://github.com/py-pdf/pypdf/pull/3892
- https://github.com/py-pdf/pypdf/commit/5a33a46416aa1ae6c025ff90a3cca57631fdafd2
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.14.2
