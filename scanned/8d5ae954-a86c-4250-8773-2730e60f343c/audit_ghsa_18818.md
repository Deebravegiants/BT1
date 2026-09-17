# [H] vLLM is vulnerable to timing attack at bearer auth

## Summary
Severity: High
Advisory: GHSA-wr9h-g72x-mwhm
CVE: CVE-2025-59425
CWE: CWE-385
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-wr9h-g72x-mwhm
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.11.0

## Details
### Summary
The API key support in vLLM performed validation using a method that was vulnerable to a timing attack. This could potentially allow an attacker to discover a valid API key using an approach more efficient than brute force.

### Details
https://github.com/vllm-project/vllm/blob/4b946d693e0af15740e9ca9c0e059d5f333b1083/vllm/entrypoints/openai/api_server.py#L1270-L1274

API key validation used a string comparison that will take longer the more characters the provided API key gets correct. Data analysis across many attempts can allow an attacker to determine when it finds the next correct character in the key sequence.
 
### Impact
Deployments relying on vLLM's built-in API key validation are vulnerable to authentication bypass using this technique.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-wr9h-g72x-mwhm
- https://nvd.nist.gov/vuln/detail/CVE-2025-59425
- https://github.com/vllm-project/vllm/commit/ee10d7e6ff5875386c7f136ce8b5f525c8fcef48
- https://github.com/advisories/GHSA-wr9h-g72x-mwhm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2026.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/4b946d693e0af15740e9ca9c0e059d5f333b1083/vllm/entrypoints/openai/api_server.py#L1270-L1274
- https://github.com/vllm-project/vllm/releases/tag/v0.11.0
- https://pypi.org/project/vllm
