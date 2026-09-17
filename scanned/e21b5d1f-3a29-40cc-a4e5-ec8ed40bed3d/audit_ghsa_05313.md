# [M] Docling: Unsafe Archive Extraction and XML Parsing in METS-GBS Backend

## Summary
Severity: Medium
Advisory: GHSA-r3xg-rg9j-67fv
CVE: CVE-2026-44018
CWE: CWE-409, CWE-611, CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-r3xg-rg9j-67fv
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=2.45.0 <2.91.0

## Details
### Impact
The METS-GBS backend's XML parsing and the input document format detection lacked security controls, enabling:
- XML External Entity (XXE) attacks to read local files or cause denial of service
- Decompression bombs (zip bombs) to exhaust memory and disk space
- Unbounded archive extraction consuming system resources

An attacker could craft malicious METS-GBS archives that, when processed, could read sensitive files, exhaust system resources, or cause application crashes.

### Patches
Fixed in version 2.91.0. The fix implements:
- Secure XML parsing with `resolve_entities=False`, `load_dtd=False`, and `no_network=True`
- Configurable limits: 300 MB total extraction size, 10 MB per file, 1000 member count
- Cumulative size tracking across all extractions
- Early termination when limits are exceeded
- Secure format detection of METS-GBS tar archives with `_detect_mets_gbs()` method: maximum file size (10 MB per file), maximum member count (1000 members), and exception handling to gracefully fail when limits are exceeded

### Workarounds
Avoid processing METS-GBS archives from untrusted sources. If necessary, pre-validate archives in an isolated environment with resource limits.

### References
- Fix release: [v2.91.0](https://github.com/docling-project/docling/releases/tag/v2.91.0)

## References
- https://github.com/docling-project/docling/security/advisories/GHSA-r3xg-rg9j-67fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44018
- https://github.com/docling-project/docling
- https://github.com/docling-project/docling/releases/tag/v2.91.0
- https://github.com/pypa/advisory-database/tree/main/vulns/docling/PYSEC-2026-2144.yaml
