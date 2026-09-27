# [M] Docling: Potential Path Traversal via LaTeX \includegraphics and \input Commands

## Summary
Severity: Medium
Advisory: GHSA-2j5p-7p5m-cvqr
CVE: CVE-2026-44022
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-2j5p-7p5m-cvqr
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=2.73.0 <2.91.0

## Details
### Impact
The LaTeX backend's handling of `\includegraphics`, `\input`, and `\include` commands lacked path containment validation. Attackers could craft malicious LaTeX documents with path traversal sequences (e.g., `../../../etc/passwd`) to:
- Read arbitrary files from the file system accessible to the process
- Include sensitive files in the converted document output
- Potentially access configuration files, credentials, or other sensitive data

### Patches
Fixed in version 2.91.0. The fix implements strict path validation using `Path.resolve().is_relative_to()` to ensure all resolved paths remain within the base document directory. Attempts to traverse outside the base directory are logged and blocked.

### Workarounds
Avoid processing untrusted LaTeX documents. If processing is necessary, run in a sandboxed environment with restricted file system access.

### References
- Fix release: [v2.91.0](https://github.com/docling-project/docling/releases/tag/v2.91.0)

## References
- https://github.com/docling-project/docling/security/advisories/GHSA-2j5p-7p5m-cvqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44022
- https://github.com/docling-project/docling
- https://github.com/docling-project/docling/releases/tag/v2.91.0
- https://github.com/pypa/advisory-database/tree/main/vulns/docling/PYSEC-2026-2145.yaml
