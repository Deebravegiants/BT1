# [M] vLLM: Unauthenticated Internal Path and Username Disclosure via Validation Error Messages

## Summary
Severity: Medium
Advisory: CVE-2026-73555
Aliases: GHSA-hwrm-c4cx-rf4j, PYSEC-2026-3937
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73555
Type: osv

## Details
vLLM is an inference and serving engine for large language models. Prior to 0.26.0, the validation_exception_handler in vllm/entrypoints/openai/server_utils.py converts FastAPI RequestValidationError objects with str(exc), and sanitize_message in vllm/entrypoints/utils.py does not remove traceback-style file paths, allowing unauthenticated malformed JSON requests to /v1/chat/completions, /v1/completions, /tokenize, and /detokenize to disclose the OS username, home and virtual-environment paths, Python version, internal package structure, line numbers, and endpoint handler names. This issue is fixed in version 0.26.0.

## References
- https://github.com/vllm-project/vllm/releases/tag/v0.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73555.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-hwrm-c4cx-rf4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73555
- https://github.com/vllm-project/vllm/commit/e87521626febe2763f997691d1599de4175f4324
- https://github.com/vllm-project/vllm/pull/46415
