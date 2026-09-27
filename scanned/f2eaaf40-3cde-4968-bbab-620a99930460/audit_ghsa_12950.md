# [C] llama-index vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-2xxc-73fv-36f7
CVE: CVE-2023-39662
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-15
Source: https://github.com/advisories/GHSA-2xxc-73fv-36f7
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.9.14

## Details
An issue in llama_index v.0.7.13 and before allows a remote attacker to execute arbitrary code via the `exec` parameter in PandasQueryEngine function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39662
- https://github.com/jerryjliu/llama_index/issues/7054
- https://github.com/run-llama/llama_index/commit/9f3e50a803f519af9ab62e63d413441c43001d81
- https://github.com/run-llama/llama_index/commit/aa6726706476e0f957a8d57a5ca89e519e93bad7
- https://github.com/jerryjliu/llama_index
- https://github.com/pypa/advisory-database/tree/main/vulns/llama-index/PYSEC-2023-148.yaml
