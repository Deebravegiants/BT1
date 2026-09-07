# [C] llama_index vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-v3c8-3pr6-gr7p
CVE: CVE-2025-1793
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-v3c8-3pr6-gr7p
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.12.28

## Details
Multiple vector store integrations in run-llama/llama_index version v0.12.21 have SQL injection vulnerabilities. These vulnerabilities allow an attacker to read and write data using SQL, potentially leading to unauthorized access to data of other users depending on the usage of the llama-index library in a web application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1793
- https://github.com/run-llama/llama_index/commit/0008041e8dde8e519621388e5d6f558bde6ef42e
- https://github.com/advisories/GHSA-v3c8-3pr6-gr7p
- https://github.com/pypa/advisory-database/tree/main/vulns/llama-index/PYSEC-2026-394.yaml
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/8cb1555a-9655-4122-b0d6-60059e79183c
- https://pypi.org/project/llama-index
