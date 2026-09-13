# [H] Tornado: Quadratic DoS via Crafted Multipart Parameters

## Summary
Severity: High
Advisory: GHSA-jhmp-mqwm-3gq8
CVE: CVE-2025-67726
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-jhmp-mqwm-3gq8
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.3

## Details
## Summary

The `_parseparam` function in Tornado's `httputil.py` is used to parse specific HTTP header values, such as those in `multipart/form-data`. This function uses an inefficient algorithm that repeatedly calls `string.count()` within a nested loop while processing quoted semicolons (e.g., `param=";"`).

As a result, if an attacker sends a request with a large number of maliciously crafted parameters in a `Content-Disposition` header, the server's CPU usage increases quadratically (O(n²)) during parsing. Due to Tornado's single event loop architecture, a single malicious request can cause the entire server to become unresponsive for an extended period, leading to a Denial of Service (DoS).

**Severity: High**

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-jhmp-mqwm-3gq8
- https://nvd.nist.gov/vuln/detail/CVE-2025-67726
- https://github.com/tornadoweb/tornado/commit/771472cfdaeebc0d89a9cc46e249f8891a6b29cd
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2025-267.yaml
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.3
