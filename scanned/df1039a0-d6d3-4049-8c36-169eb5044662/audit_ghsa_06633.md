# [H] vLLM denial of service via prompt embeds on M-RoPE models

## Summary
Severity: High
Advisory: GHSA-33cg-gxv8-3p8g
CVE: CVE-2026-55514
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-33cg-gxv8-3p8g
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.12.0 <0.24.0

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible. For example: An unsafe deserialization vulnerability allows any unauthenticated user to execute arbitrary code on the server._

Sending a pure prompt embeds payload in a `/v1/completions` request with a model using M-RoPE causes the EngineCore to fail an assertion and fatally crash, shutting down the entire server application.

Any remote user who is authorized to make a `/v1/completions` endpoint can trivially make such a request and induce a crash.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

In commit [56669c1](https://github.com/vllm-project/vllm/commit/56669c1f293d5c53b6a19ddf2f78802fa9fff2c2), a simple assert intended to be a type-narrowing assert was added to the `_init_mrope_positions` method in `GPUModelRunner` (the offending line on main at the time of writing: https://github.com/vllm-project/vllm/blob/2d481f8a946ee0521872af0f098674a8ee01ce4a/vllm/v1/worker/gpu_model_runner.py#L1588-L1607).

```python
assert req_state.prompt_token_ids is not None, (
            "M-RoPE requires prompt_token_ids to be available."
        )
```

This type narrowing assert is to prevent mypy errors later in the function because `None` is not a valid type for `mrope_model.get_mrope_input_positions`. Unfortunately, this assertion is not always true. `/v1/completions` requests that specify `prompt=None` and `prompt_embeds=<not none>` will indeed create a CachedRequestState where `prompt_token_ids` is `None`. This triggers the assertion, which in turn crashes the EngineCore and the Server application.

```
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]   File "/usr/local/lib/python3.12/dist-packages/vllm/v1/worker/gpu_model_runner.py", line 3997, in execute_model
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]     deferred_state_corrections_fn = self._update_states(scheduler_output)
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]   File "/usr/local/lib/python3.12/dist-packages/vllm/v1/worker/gpu_model_runner.py", line 1239, in _update_states
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]     self._init_mrope_positions(req_state)
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]   File "/usr/local/lib/python3.12/dist-packages/vllm/v1/worker/gpu_model_runner.py", line 1582, in _init_mrope_positions
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]     assert req_state.prompt_token_ids is not None, (
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(EngineCore pid=351) ERROR 06-11 00:48:03 [core.py:1167] AssertionError: M-RoPE requires prompt_token_ids to be available.
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704] AsyncLLM output_handler failed.
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704] Traceback (most recent call last):
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704]   File "/usr/local/lib/python3.12/dist-packages/vllm/v1/engine/async_llm.py", line 660, in output_handler
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704]     outputs = await engine_core.get_output_async()
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704]               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704]   File "/usr/local/lib/python3.12/dist-packages/vllm/v1/engine/core_client.py", line 1030, in get_output_async
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704]     raise self._format_exception(outputs) from None
(APIServer pid=1) ERROR 06-11 00:48:03 [async_llm.py:704] vllm.v1.engine.exceptions.EngineDeadError: EngineCore encountered an issue. See stack trace (above) for the root cause.
```

All requests using the `/v1/chat/completions` endpoints will have text/`prompt_token_ids` parts (corresponding to the chat template), and `prompt_embeds` parts are handled as mm_features. This method (rightly) filters out those `prompt_embeds` content parts as they are treated as text positions.

A sufficient solution to type narrowing here without raising a fatal assertion is to instead replace the assertion with a using dummy token ids:

```python
def _init_mrope_positions(self, req_state: CachedRequestState):
    model = self.get_model()
    assert supports_mrope(model), "M-RoPE support is not implemented."
    mrope_model = cast(SupportsMRoPE, model)

    # Filter out prompt_embeds modality (text-only position info)
    mrope_features = [
        f for f in req_state.mm_features if f.modality != "prompt_embeds"
    ]
    
    # Handle both token_ids and embeddings-only inputs
    if req_state.prompt_token_ids is not None:
        input_tokens = req_state.prompt_token_ids
    elif req_state.prompt_embeds is not None:
        # For text-only embeddings, dummy token IDs are safe since
        # get_mrope_input_positions only uses len(input_tokens) when mm_features is empty
        seq_len = req_state.prompt_embeds.shape[0]
        input_tokens = list(range(seq_len))
        # Verify no mm_features remain (should be true after prompt_embeds filter)
        assert len(mrope_features) == 0, (
            "M-RoPE with prompt_embeds-only input should have no multimodal features"
        )
    else:
        raise ValueError(
            "M-RoPE requires either prompt_token_ids or prompt_embeds."
        )

    req_state.mrope_positions, req_state.mrope_position_delta = (
        mrope_model.get_mrope_input_positions(
            input_tokens,
            mrope_features,
        )
    )
```

Technically, in isolation, this method still crashes in the case where `req_state.prompt_token_ids is None and req_state.mm_features`, so the solution above still leaves that potential vector open. As far as can be determined, however, such a `req_state` is impossible in the first place in online mode, because it would require a `/v1/completions` request with `prompt_embeds` AND multimodal features, but the `/v1/completions` request schema does not expose multimodal inputs in any discernible way. Today, those are the only two endpoints with `prompt_embeds` support. 

When in offline mode, it *is technically* possible to directly create an `EngineCoreRequest` that has `prompt_embeds and not prompt_token_ids and mm_features`, and pass that to `LLM.generate`. That would trigger this same assertion, and no validation would prevent that combination. It is strongly suspected, though, that this combination would be undefined in any model that support M-RoPE, because it would not be possible to determine which token positions correspond to `mm_features`. The proposed solution above would end up not setting `req_state.mrope_positions` and `req_state.mrope_position_delta` in this scenario, which could result in undefined behavior.

`prompt_embeds` is far more familiar here than M-RoPE, and it is understood that each model that supports it is responsible for defining its own `get_mrope_input_positions` which have varying implementations. There is insufficient knowledge to be prescriptive in how the two features should interact in the offline case, other than possibly raising a validation error earlier on preventing that combination (which would emulate the current assertion behavior). Regardless, in offline mode, the chances of a remote user being able to exploit this are slim-to-nil compared to the online case which is incredibly straightforward.

### Impact
_What kind of vulnerability is it? Who is impacted?_

- Denial of Service caused by an incorrect assertion inside of the `GPUModelRunner` which causes a fatal EngineCore exception
- Any configuration with `--enable-prompt-embeds` and M-RoPE-supported model is vulnerable
- The attack is extremely easy from the remote attacker's perspective (copying the official `prompt_embeds` online mode docs examples almost-verbatim, accounting for model-name and connection details, of course, will induce a guaranteed shutdown)

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-33cg-gxv8-3p8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-55514
- https://github.com/vllm-project/vllm/pull/45252
- https://github.com/vllm-project/vllm/commit/470229c37efaf69c86e8bc97482b0b1ff7551c65
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2303.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/releases/tag/v0.24.0
