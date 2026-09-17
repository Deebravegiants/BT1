# [M] vLLM vulnerable to Denial of Service by abusing xgrammar cache

## Summary
Severity: Medium
Advisory: GHSA-hf3c-wxg2-49q9
CWE: CWE-1395, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-15
Source: https://github.com/advisories/GHSA-hf3c-wxg2-49q9
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.6.5 <0.8.4

## Details
### Impact

This report is to highlight a vulnerability in XGrammar, a library used by the structured output feature in vLLM. The XGrammar advisory is here: https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-389x-67px-mjg3

The [xgrammar](https://xgrammar.mlc.ai/docs/) library is the default backend used by vLLM to support structured output (a.k.a. guided decoding). Xgrammar provides a required, built-in cache for its compiled grammars stored in RAM. xgrammar is available by default through the OpenAI compatible API server with both the V0 and V1 engines.

A malicious user can send a stream of very short decoding requests with unique schemas, resulting in an addition to the cache for each request. This can result in a Denial of Service by consuming all of the system's RAM.

Note that even if vLLM was configured to use a different backend by default, it is still possible to choose xgrammar on a per-request basis using the `guided_decoding_backend` key of the `extra_body` field of the request with the V0 engine. This per-request choice is not available when using the V1 engine. 
### Patches

* https://github.com/vllm-project/vllm/pull/16283

### Workarounds

There is no way to workaround this issue in existing versions of vLLM other than preventing untrusted access to the OpenAI compatible API server.

### References

* https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-389x-67px-mjg3

## References
- https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-389x-67px-mjg3
- https://github.com/vllm-project/vllm/security/advisories/GHSA-hf3c-wxg2-49q9
- https://github.com/vllm-project/vllm/pull/16283
- https://github.com/vllm-project/vllm/commit/cb84e45ac75b42ba6795145923e8eb323bb825ad
- https://github.com/vllm-project/vllm
