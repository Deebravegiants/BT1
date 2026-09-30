# [M] vLLM allows clients to crash the openai server with invalid regex

## Summary
Severity: Medium
Advisory: GHSA-9hcf-v7m4-6m2j
CVE: CVE-2025-48943
CWE: CWE-248
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-9hcf-v7m4-6m2j
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.8.0 <0.9.0

## Details
### Impact

A denial of service bug caused the vLLM server to crash if an invalid regex was provided while using structured output. This vulnerability is similar to [GHSA-6qc9-v4r8-22xg](https://github.com/vllm-project/vllm/security/advisories/GHSA-6qc9-v4r8-22xg), but for regex instead of a JSON schema.

Issue with more details: https://github.com/vllm-project/vllm/issues/17313

### Patches

* https://github.com/vllm-project/vllm/pull/17623

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-9hcf-v7m4-6m2j
- https://nvd.nist.gov/vuln/detail/CVE-2025-48943
- https://github.com/vllm-project/vllm/issues/17313
- https://github.com/vllm-project/vllm/pull/17623
- https://github.com/vllm-project/vllm/commit/08bf7840780980c7568c573c70a6a8db94fd45ff
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2025-55.yaml
- https://github.com/vllm-project/vllm
