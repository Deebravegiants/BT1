# [M] vLLM: ReDoS via structured_outputs.regex in the lm-format-enforcer backend (no compile timeout) — missed sibling of CVE-2026-55574

## Summary
Severity: Medium
Advisory: CVE-2026-73556
Aliases: GHSA-48jh-3gj7-fg8v, PYSEC-2026-3933
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73556
Type: osv

## Details
vLLM is an inference and serving engine for large language models. Prior to 0.26.0, the structured_outputs.regex parameter in vllm/v1/structured_output/backend_lm_format_enforcer.py is passed to lmformatenforcer.RegexParser without compile_regex_with_timeout or validation in validate_structured_output_request_lm_format_enforcer, allowing an unauthenticated /v1/completions request against the lm-format-enforcer backend to consume a CPU core and stall the structured-output engine path with a catastrophic regular expression. This issue is fixed in version 0.26.0.

## References
- https://github.com/vllm-project/vllm/releases/tag/v0.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73556.json
- https://github.com/vllm-project/vllm/security/advisories/GHSA-48jh-3gj7-fg8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-73556
- https://github.com/vllm-project/vllm/commit/c9a788eedc412acceaa5112e0d44624b49841577
- https://github.com/vllm-project/vllm/pull/47595
