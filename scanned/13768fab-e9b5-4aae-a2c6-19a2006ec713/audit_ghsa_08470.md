# [M] vLLM: extract_hidden_states speculative decoding crashes server on any request with penalty parameters

## Summary
Severity: Medium
Advisory: GHSA-83vm-p52w-f9pw
CVE: CVE-2026-44223
CWE: CWE-131, CWE-704
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-83vm-p52w-f9pw
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.18.0 <0.20.0

## Details
### Summary

The `extract_hidden_states` speculative decoding proposer in vLLM returns a tensor with an incorrect shape after the first decode step, causing a `RuntimeError` that crashes the EngineCore process. The crash is triggered when any request in the batch uses sampling penalty parameters (`repetition_penalty`, `frequency_penalty`, or `presence_penalty`).

A single request with a penalty parameter (e.g., `"repetition_penalty": 1.1`) is sufficient to crash the server. The crash is deterministic and immediate — no concurrency, race condition, or special workload is required.

### Details

In vLLM v0.17.0, the `extract_hidden_states` proposer's `propose()` method returned `sampled_token_ids.unsqueeze(-1)`, producing a tensor of shape `(batch_size, 1)`.

In [PR #37013](https://github.com/vllm-project/vllm/pull/37013) (first released in v0.18.0), the KV connector interface was refactored out of `propose()`. The return type changed from `tuple[Tensor, KVConnectorOutput | None]` to `Tensor`, and the `.unsqueeze(-1)` call was removed along with the KV connector output:

```python
# Before (v0.17.0):
return sampled_token_ids.unsqueeze(-1), kv_connector_output  # shape (batch_size, 1)

# After (v0.18.0+):
return sampled_token_ids  # shape (batch_size, 2) after first decode step
```

The refactor missed that `sampled_token_ids` changed semantics between the first and subsequent decode steps. After the first decode step, the rejection sampler allocates its output as `(batch_size, max_spec_len + 1)`. With `num_speculative_tokens=1`, this produces shape `(batch_size, 2)` instead of the expected `(batch_size, 1)`, causing a broadcast shape mismatch during penalty application.

### Impact

Any vLLM deployment between v0.18.0 and v0.19.1 (inclusive) configured with `extract_hidden_states` speculative decoding is affected. A single API request containing any penalty parameter immediately and permanently crashes the EngineCore process, resulting in complete loss of service availability.

### Patches

Fixed in [PR #38610](https://github.com/vllm-project/vllm/pull/38610), first included in vLLM v0.20.0. The fix slices the return value to `sampled_token_ids[:, :1]`, ensuring the correct `(batch_size, 1)` shape regardless of the rejection sampler's output dimensions.

### Workarounds

- Upgrade to vLLM v0.20.0 or later.
- If upgrading is not possible, avoid using `extract_hidden_states` as the speculative decoding method on affected versions.
- Alternatively, reject or strip penalty parameters (`repetition_penalty`, `frequency_penalty`, `presence_penalty`) from incoming requests at an API gateway before they reach vLLM.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-83vm-p52w-f9pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44223
- https://github.com/vllm-project/vllm/pull/38610
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-145.yaml
- https://github.com/vllm-project/vllm
