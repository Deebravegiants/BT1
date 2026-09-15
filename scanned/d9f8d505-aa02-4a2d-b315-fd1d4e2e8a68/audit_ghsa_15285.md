# [C] LlamaIndex includes an exec call for `import {cls_name}`

## Summary
Severity: Critical
Advisory: GHSA-fxc2-8m62-m85x
CVE: CVE-2024-45201
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-fxc2-8m62-m85x
Type: github-advisory

## Affected
- PyPI: `llama-index-core` — affected >=0 <0.10.38

## Details
An issue was discovered in llama_index before 0.10.38. `download/integration.py` includes an exec call for `import {cls_name}`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45201
- https://github.com/run-llama/llama_index/pull/13523
- https://github.com/run-llama/llama_index/commit/bd827c30484fa085ec769fa55dc7f2add8006ac8
- https://github.com/pypa/advisory-database/tree/main/vulns/llama-index/PYSEC-2024-192.yaml
- https://github.com/run-llama/llama_index
- https://github.com/run-llama/llama_index/compare/v0.10.37...v0.10.38
