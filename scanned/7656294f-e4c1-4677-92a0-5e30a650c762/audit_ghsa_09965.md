# [M] vLLM: Unauthenticated OOM Denial of Service via Unbounded `n` Parameter in OpenAI API Server

## Summary
Severity: Medium
Advisory: GHSA-3mwp-wvh9-7528
CVE: CVE-2026-34756
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-3mwp-wvh9-7528
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.1.0 <0.19.0

## Details
### Summary
A Denial of Service vulnerability exists in the vLLM OpenAI-compatible API server. Due to the lack of an upper bound validation on the `n` parameter in the `ChatCompletionRequest` and `CompletionRequest` Pydantic models, an unauthenticated attacker can send a single HTTP request with an astronomically large `n` value. This completely blocks the Python `asyncio` event loop and causes immediate Out-Of-Memory crashes by allocating millions of request object copies in the heap before the request even reaches the scheduling queue.

### Details
The root cause of this vulnerability lies in the missing upper bound checks across the request parsing and asynchronous scheduling layers:

1. **Protocol Layer:**
   In `vllm/entrypoints/openai/chat_completion/protocol.py`, the `n` parameter is defined simply as an integer without any `pydantic.Field` constraints for an upper bound.
```python
class ChatCompletionRequest(OpenAIBaseModel):
    # Ordered by official OpenAI API documentation
    # https://platform.openai.com/docs/api/reference/chat/create
    messages: list[ChatCompletionMessageParam]
    model: str | None = None
    frequency_penalty: float | None = 0.0
    logit_bias: dict[str, float] | None = None
    logprobs: bool | None = False
    top_logprobs: int | None = 0
    max_tokens: int | None = Field(
        default=None,
        deprecated="max_tokens is deprecated in favor of "
        "the max_completion_tokens field",
    )
    max_completion_tokens: int | None = None
    n: int | None = 1
    presence_penalty: float | None = 0.0
```

1. **SamplingParams Layer (Incomplete Validation):**
   When the API request is converted to internal `SamplingParams` in `vllm/sampling_params.py`, the `_verify_args` method only checks the lower bound (`self.n < 1`), entirely omitting an upper bounds check.
```python
    def _verify_args(self) -> None:
        if not isinstance(self.n, int):
            raise ValueError(f"n must be an int, but is of type {type(self.n)}")
        if self.n < 1:
            raise ValueError(f"n must be at least 1, got {self.n}.")
```

1. **Engine Layer (The OOM Trigger):**
   When the malicious request reaches the core engine (`vllm/v1/engine/async_llm.py`), the engine attempts to fan out the request `n` times to generate identical independent sequences within a synchronous loop.
```python
        # Fan out child requests (for n>1).
        parent_request = ParentRequest(request)
        for idx in range(parent_params.n):
            request_id, child_params = parent_request.get_child_info(idx)
            child_request = request if idx == parent_params.n - 1 else copy(request)
            child_request.request_id = request_id
            child_request.sampling_params = child_params
            await self._add_request(
                child_request, prompt_text, parent_request, idx, queue
            )
        return queue
```
   Because Python's `asyncio` runs on a single thread and event loop, this monolithic `for`-loop monopolizes the CPU thread. The server stops responding to all other connections (including liveness probes). Simultaneously, the memory allocator is overwhelmed by cloning millions of request object instances via `copy(request)`, driving the host's Resident Set Size (RSS) up by gigabytes per second until the OS `OOM-killer` terminates the vLLM process.

### Impact
**Vulnerability Type:** Resource Exhaustion / Denial of Service

**Impacted Parties:**
- Any individual or organization hosting a public-facing vLLM API server (`vllm.entrypoints.openai.api_server`), which happens to be the primary entrypoint for OpenAI-compatible setups.
- SaaS / AI-as-a-Service platforms acting as reverse proxies sitting in front of vLLM without strict HTTP body payload validation or rate limitations.

Because this vulnerability exploits the control plane rather than the data plane, an unauthenticated remote attacker can achieve a high success rate in taking down production inference hosts with a single HTTP request. This effectively circumvents any hardware-level capacity planning and conventional bandwidth stress limitations.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-3mwp-wvh9-7528
- https://nvd.nist.gov/vuln/detail/CVE-2026-34756
- https://github.com/vllm-project/vllm/pull/37952
- https://github.com/vllm-project/vllm/commit/b111f8a61f100fdca08706f41f29ef3548de7380
- https://access.redhat.com/errata/RHSA-2026:36005
- https://access.redhat.com/errata/RHSA-2026:36006
- https://access.redhat.com/security/cve/CVE-2026-34756
- https://bugzilla.redhat.com/show_bug.cgi?id=2455425
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2298.yaml
- https://github.com/vllm-project/vllm
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34756.json
