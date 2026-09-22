# [H] Tornado: Quadratic DoS via Repeated Header Coalescing

## Summary
Severity: High
Advisory: GHSA-c98p-7wgm-6p64
CVE: CVE-2025-67725
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-c98p-7wgm-6p64
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.3

## Details
## Summary

The `HTTPHeaders.add` method in Tornado accumulates values using string concatenation when the same header name is repeated. Due to Python string immutability, each concatenation copies the entire string, resulting in O(n²) time complexity.

Given Tornado's single event loop architecture, a single maliciously crafted HTTP request can block the server's event loop for an extended period, causing a Denial of Service (DoS).

**Severity:**  **High** if `max_header_size` has been increased from its default, **low** if it has its default value of 64KB.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-c98p-7wgm-6p64
- https://nvd.nist.gov/vuln/detail/CVE-2025-67725
- https://github.com/tornadoweb/tornado/commit/771472cfdaeebc0d89a9cc46e249f8891a6b29cd
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2025-266.yaml
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.3
