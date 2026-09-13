# [H] LlamaIndex vulnerable to Creation of Temporary File in Directory with Insecure Permissions

## Summary
Severity: High
Advisory: GHSA-jmgm-gx32-vp4w
CVE: CVE-2024-12911
CWE: CWE-379, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-jmgm-gx32-vp4w
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.12.3

## Details
A vulnerability in the `default_jsonalyzer` function of the `JSONalyzeQueryEngine` in the run-llama/llama_index repository allows for SQL injection via prompt injection. This can lead to arbitrary file creation and Denial-of-Service (DoS) attacks. The vulnerability affects the latest version and is fixed in version 0.12.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12911
- https://github.com/run-llama/llama_index/commit/bf282074e20e7dafd5e2066137dcd4cd17c3fb9e
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/095f9e67-311d-494c-99c5-5e61a0adb8f3
