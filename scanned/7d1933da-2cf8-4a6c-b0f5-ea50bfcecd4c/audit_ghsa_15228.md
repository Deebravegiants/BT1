# [C] Unsafe yaml deserialization in llama-hub

## Summary
Severity: Critical
Advisory: GHSA-297x-2qf3-jrj3
CVE: CVE-2024-23730
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-21
Source: https://github.com/advisories/GHSA-297x-2qf3-jrj3
Type: github-advisory

## Affected
- PyPI: `llama-hub` — affected >=0 <0.0.67

## Details
The OpenAPI and ChatGPT plugin loaders in LlamaHub (aka llama-hub) before 0.0.67 allow attackers to execute arbitrary code because safe_load is not used for YAML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23730
- https://github.com/run-llama/llama-hub/pull/841/commits/9dc9c21a5c6d0226d1d2101c3121d4f085743d52
- https://github.com/run-llama/llama-hub/commit/c01416e737c7747a213a79881b8308c41d043515
- https://github.com/run-llama/llama-hub
- https://github.com/run-llama/llama-hub/blob/v0.0.67/CHANGELOG.md
- https://github.com/run-llama/llama-hub/releases/tag/v0.0.67
