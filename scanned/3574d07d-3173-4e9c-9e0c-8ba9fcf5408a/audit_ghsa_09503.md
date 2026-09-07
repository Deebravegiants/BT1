# [M] Pillow has a PDF Parsing Trailer Infinite Loop (DoS)

## Summary
Severity: Medium
Advisory: GHSA-r73j-pqj5-w3x7
CVE: CVE-2026-42310
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-r73j-pqj5-w3x7
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=4.2.0 <12.2.0

## Details
### Impact
An attacker can supply a malicious PDF that causes the process to hang indefinitely, consuming 100% CPU and making the application unresponsive.

### Patches
Patched version: 12.2.0.

PdfParser (introduced in Pillow 4.2.0) follows Prev pointers in PDF trailers to read cross-reference sections. If a
trailer's Prev pointer references an offset that has already been processed — either pointing to itself or forming a
longer cycle — the parser enters an infinite loop. Pillow now tracks previously processed trailer offsets and raises an
error if a cycle is detected.

### Workarounds
Use any version but the affected versions: >= 4.2.0, < 12.2.0

### Resources
 - Fix: https://github.com/python-pillow/Pillow/pull/9519

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-r73j-pqj5-w3x7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42310
- https://github.com/python-pillow/Pillow/pull/9519
- https://github.com/python-pillow/Pillow/commit/3bf614e4b8615d0ce1d5039efaf6db447fe7c468
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.2.0
