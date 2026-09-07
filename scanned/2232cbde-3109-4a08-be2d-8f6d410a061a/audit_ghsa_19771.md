# [M] vLLM denial of service via outlines unbounded cache on disk

## Summary
Severity: Medium
Advisory: GHSA-mgrm-fgjv-mhv8
CVE: CVE-2025-29770
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-mgrm-fgjv-mhv8
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.8.0

## Details
### Impact
The [outlines](https://dottxt-ai.github.io/outlines/latest/) library is one of the backends used by vLLM to support structured output (a.k.a. guided decoding). Outlines provides an optional cache for its compiled grammars on the local filesystem. This cache has been on by default in vLLM. Outlines is also available by default through the OpenAI compatible API server.

The affected code in vLLM is [vllm/model_executor/guided_decoding/outlines_logits_processors.py](https://github.com/vllm-project/vllm/blob/53be4a863486d02bd96a59c674bbec23eec508f6/vllm/model_executor/guided_decoding/outlines_logits_processors.py), which unconditionally uses the cache from outlines. vLLM should have this off by default and allow administrators to opt-in due to the potential for abuse.

A malicious user can send a stream of very short decoding requests with unique schemas, resulting in an addition to the cache for each request. This can result in a Denial of Service if the filesystem runs out of space.

Note that even if vLLM was configured to use a different backend by default, it is still possible to choose outlines on a per-request basis using the `guided_decoding_backend` key of the `extra_body` field of the request.

This issue applies to the V0 engine only. The V1 engine is not affected.

### Patches

* https://github.com/vllm-project/vllm/pull/14837

The fix is to disable this cache by default since it does not provide an option to limit its size. If you want to use this cache anyway, you may set the `VLLM_V0_USE_OUTLINES_CACHE` environment variable to `1`.

### Workarounds

There is no way to workaround this issue in existing versions of vLLM other than preventing untrusted access to the OpenAI compatible API server.

### References

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-mgrm-fgjv-mhv8
- https://nvd.nist.gov/vuln/detail/CVE-2025-29770
- https://github.com/vllm-project/vllm/pull/14837
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2025-223.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/53be4a863486d02bd96a59c674bbec23eec508f6/vllm/model_executor/guided_decoding/outlines_logits_processors.py
