# [H] vLLM:  Dependency Confusion Vulnerability in vLLM Dockerfile

## Summary
Severity: High
Advisory: CVE-2026-54232
Aliases: GHSA-jrf6-vqxq-pjv2, PYSEC-2026-227
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-54232
Type: osv

## Details
vLLM is an inference and serving engine for large language models (LLMs). Prior to 0.22.1, the vLLM Dockerfile is vulnerable to a dependency confusion attack through the flashinfer-jit-cache package. The package is installed from a custom index (flashinfer.ai/whl/) using --extra-index-url, but the package name was not registered on PyPI, and UV_INDEX_STRATEGY="unsafe-best-match" is set globally. An attacker who registers flashinfer-jit-cache on PyPI with version 0.6.11.post2 can execute arbitrary code as root during the Docker build and backdoor every resulting container image, enabling exfiltration of all user prompts, API credentials, and model data from production vLLM deployments This vulnerability is fixed in 0.22.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54232.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-jrf6-vqxq-pjv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-54232
