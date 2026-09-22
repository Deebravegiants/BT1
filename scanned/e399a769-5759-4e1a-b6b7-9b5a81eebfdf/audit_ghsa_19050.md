# [M] vLLM vulnerable to DoS via large Chat Completion or Tokenization requests with specially crafted `chat_template_kwargs`

## Summary
Severity: Medium
Advisory: GHSA-69j4-grxj-j64p
CVE: CVE-2025-62426
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-69j4-grxj-j64p
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.5.5 <0.11.1

## Details
### Summary
The /v1/chat/completions and /tokenize endpoints allow a `chat_template_kwargs` request parameter that is used in the code before it is properly validated against the chat template. With the right `chat_template_kwargs` parameters, it is possible to block processing of the API server for long periods of time, delaying all other requests 

### Details
In serving_engine.py, the chat_template_kwargs are unpacked into kwargs passed to chat_utils.py `apply_hf_chat_template` with no validation on the keys or values in that chat_template_kwargs dict. This means they can be used to override optional parameters in the `apply_hf_chat_template` method, such as `tokenize`, changing its default from False to True.

https://github.com/vllm-project/vllm/blob/2a6dc67eb520ddb9c4138d8b35ed6fe6226997fb/vllm/entrypoints/openai/serving_engine.py#L809-L814

https://github.com/vllm-project/vllm/blob/2a6dc67eb520ddb9c4138d8b35ed6fe6226997fb/vllm/entrypoints/chat_utils.py#L1602-L1610

Both serving_chat.py and serving_tokenization.py call into this `_preprocess_chat` method of `serving_engine.py` and they both pass in `chat_template_kwargs`.

So, a `chat_template_kwargs` like `{"tokenize": True}` makes tokenization happen as part of applying the chat template, even though that is not expected. Tokenization is a blocking operation, and with sufficiently large input can block the API server's event loop, which blocks handling of all other requests until this tokenization is complete.

This optional `tokenize` parameter to `apply_hf_chat_template` does not appear to be used, so one option would be to just hard-code that to always be False instead of allowing it to be optionally overridden by callers. A better option may be to not pass `chat_template_kwargs` as unpacked kwargs but instead as a dict, and only unpack them after the logic in `apply_hf_chat_template` that resolves the kwargs against the chat template.

### Impact

Any authenticated user can cause a denial of service to a vLLM server with Chat Completion or Tokenize requests.

### Fix

https://github.com/vllm-project/vllm/pull/27205

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-69j4-grxj-j64p
- https://nvd.nist.gov/vuln/detail/CVE-2025-62426
- https://github.com/vllm-project/vllm/pull/27205
- https://github.com/vllm-project/vllm/commit/3ada34f9cb4d1af763fdfa3b481862a93eb6bd2b
- https://github.com/advisories/GHSA-69j4-grxj-j64p
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2012.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/2a6dc67eb520ddb9c4138d8b35ed6fe6226997fb/vllm/entrypoints/chat_utils.py#L1602-L1610
- https://github.com/vllm-project/vllm/blob/2a6dc67eb520ddb9c4138d8b35ed6fe6226997fb/vllm/entrypoints/openai/serving_engine.py#L809-L814
- https://pypi.org/project/vllm
