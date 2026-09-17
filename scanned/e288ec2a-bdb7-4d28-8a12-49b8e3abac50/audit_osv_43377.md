# [M] vLLM: Cross-User Data Leak Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-73558
Aliases: GHSA-7m6h-x95x-82q5, PYSEC-2026-3935
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73558
Type: osv

## Details
vLLM is an inference and serving engine for large language models. Prior to 0.27.0, an integer overflow in blockIdx.x * 2 * d in activation_kernels.cu can cause act_and_mul_kernel to consume another batched user's input, allowing a request processed in the same inference batch to receive a partial or complete copy of another user's inference result. This issue is fixed in version 0.27.0.

## References
- https://github.com/vllm-project/vllm/releases/tag/v0.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73558.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-7m6h-x95x-82q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-73558
- https://github.com/vllm-project/vllm/issues/42860
- https://github.com/vllm-project/vllm/commit/451227cb3ff07989698fed982c2d3e4300257924
- https://github.com/vllm-project/vllm/pull/49660
