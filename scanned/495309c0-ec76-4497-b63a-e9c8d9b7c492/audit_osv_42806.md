# [M] vLLM: Derender endpoints decode caller-supplied GenerateResponse token IDs without output bounds

## Summary
Severity: Medium
Advisory: CVE-2026-71486
Aliases: GHSA-8737-qx52-hjff, PYSEC-2026-3936
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-71486
Type: osv

## Details
vLLM is an inference and serving engine for large language models. Prior to 0.26.0, the /v1/completions/derender and /v1/chat/completions/derender endpoints accept caller-supplied GenerateResponse objects whose generate_responses, choices, token_ids, prompt_logprobs, logprobs.content, top_logprobs, and routed_experts structures are processed by OnlineDerenderer and tokenizer.decode before max_model_len, max_tokens, max_num_seqs, or response-size limits are enforced, allowing an authenticated API client to consume excessive CPU and memory and produce oversized responses. This issue is fixed in version 0.26.0.

## References
- https://github.com/vllm-project/vllm/releases/tag/v0.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71486.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-8737-qx52-hjff
- https://nvd.nist.gov/vuln/detail/CVE-2026-71486
- https://github.com/vllm-project/vllm/commit/8e61b646e2d157f9b93451fa048f9c8530c8a67b
- https://github.com/vllm-project/vllm/pull/47260
