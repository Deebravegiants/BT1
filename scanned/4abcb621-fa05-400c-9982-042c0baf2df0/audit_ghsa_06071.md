# [M] vLLM: Completion prompt lists fan out into unbounded engine requests

## Summary
Severity: Medium
Advisory: GHSA-87x5-vmc3-756j
CVE: CVE-2026-73559
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-87x5-vmc3-756j
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.19.0 <0.26.0

## Details
## Summary

The `/v1/completions` request model accepts `prompt` as a list of text prompts or a list of token-id prompts without any outer prompt-count bound. The serving path turns each element into a separate engine input, creates one engine generator per element, merges all generators, and allocates a response slot per prompt. An authenticated API client can therefore turn one request into an attacker-chosen number of backend subrequests before any aggregate request-count budget is enforced.

## Technical Details

`CompletionRequest.prompt` allows both list-shaped prompt inputs and scalar prompts:

```python
# vllm/entrypoints/openai/completion/protocol.py
prompt: (
    list[Annotated[int, Field(ge=0)]]
    | list[list[Annotated[int, Field(ge=0)]]]
    | str
    | list[str]
    | None
) = None
```

The validator only requires some prompt-like input to be present:

```python
def validate_prompt_and_prompt_embeds(cls, data):
    prompt = data.get("prompt")
    prompt_embeds = data.get("prompt_embeds")
    ...
    if prompt_is_empty and embeds_is_empty:
        raise VLLMValidationError(...)
```

The renderer then expands list-shaped prompts as a sequence. `prompt_to_seq()` wraps a scalar string or a single token-id list, but returns a `list[str]` or `list[list[int]]` unchanged:

```python
# vllm/renderers/inputs/preprocess.py
def prompt_to_seq(prompt_or_prompts):
    if isinstance(prompt_or_prompts, (dict, str, bytes)) or (
        len(prompt_or_prompts) > 0 and is_list_of(prompt_or_prompts, int)
    ):
        return [prompt_or_prompts]

    return prompt_or_prompts
```

`OnlineRenderer.preprocess_completion()` appends that whole sequence, and the renderer processes every element:

```python
# vllm/renderers/online_renderer.py
prompts = list[SingletonPrompt | bytes]()
if prompt_input is not None:
    prompts.extend(prompt_to_seq(prompt_input))
...
parsed_prompts = [
    prompt if isinstance(prompt, bytes) else parse_model_prompt(model_config, prompt)
    for prompt in prompts
]
return await renderer.render_cmpl_async(parsed_prompts, tok_params, ...)
```

Finally, completion serving creates one backend generator and one response slot per rendered prompt:

```python
# vllm/entrypoints/openai/completion/serving.py
generators: list[AsyncGenerator[RequestOutput, None]] = []
for i, engine_input in enumerate(engine_inputs):
    ...
    generator = self.engine_client.generate(...)
    generators.append(generator)

result_generator = merge_async_iterators(*generators)
num_prompts = len(engine_inputs)
...
final_res_batch: list[RequestOutput | None] = [None] * num_prompts
```

The violated invariant is that one HTTP request should have a bounded backend request count. Current code enforces per-prompt token and sampling limits, but not the number of prompts in the outer completion request.

## PoV

A minimal oversized request keeps normal generation parameters small but supplies a large outer prompt list:

```json
{
  "model": "served-model",
  "prompt": ["x", "x", "x"],
  "max_tokens": 1,
  "n": 1
}
```

Scaling the `prompt` array to tens or hundreds of thousands of short entries makes the server allocate, preprocess, schedule, merge, and buffer one subrequest per entry. The same applies to token-id prompt lists:

```json
{
  "model": "served-model",
  "prompt": [[1], [1], [1]],
  "max_tokens": 1,
  "n": 1
}
```

The intended negative control is a scalar prompt:

```json
{
  "model": "served-model",
  "prompt": "x",
  "max_tokens": 1,
  "n": 1
}
```

The scalar string is wrapped as one prompt; the list form is not bounded and fans out by list length.


## Impact

An authenticated API client can make one `/v1/completions` request consume CPU, memory, async task scheduling, engine request slots, and response buffering proportional to an attacker-chosen outer prompt list. This can starve or disrupt other tenants sharing the same vLLM server. The report does not claim unauthenticated access, confidentiality impact, integrity impact, code execution, or impact where `/v1/completions` is not reachable by untrusted or semi-trusted clients.

## Suggested Fix

Reject oversized prompt lists before renderer preprocessing. Add an outer prompt-count limit to `CompletionRequest.prompt` when the prompt is `list[str]` or `list[list[int]]`, and consider making the limit configurable in the same style as the batch-chat and sampling-list bounds. The check should run before `OnlineRenderer.preprocess_completion()` expands the prompt sequence, so oversized requests do not allocate parsed prompt lists, async render/tokenization tasks, engine generators, or response result slots.

Regression coverage should include a scalar prompt, a bounded prompt list, an oversized `list[str]`, and an oversized `list[list[int]]`. The oversized requests should fail with a controlled validation error before any backend generator is created.

## Affected Package/Versions

Package ecosystem: pip

Package name: `vllm`

Affected range confirmed by source proof: `>=0.19.0, <=0.24.0`; current `main` at `cbe9c40f998f13975b967773ac7e7920e115387f` remains affected.

Patched versions: unknown.

Latest release checked: `v0.24.0`, published on 2026-06-29.

## GitHub Advisory Metadata

Package ecosystem: pip

Package name: `vllm`

Vulnerable version range: `>=0.19.0, <=0.24.0`

Patched versions: unknown

## Advisory History

Public issue and PR searches for `CompletionRequest prompt list`, `"prompt" "list[str]" "completion"`, and `"CompletionRequest" "max_length"` did not find an existing report or fix for this exact path.

The closest published advisory is `GHSA-3mwp-wvh9-7528`, "OOM Denial of Service via Unbounded `n` Parameter in OpenAI API Server", patched in `0.19.0`. This report is distinct because it keeps `n=1` and uses the `/v1/completions` `prompt` outer list to create one engine request per prompt. The fix invariant is an outer prompt-count and aggregate request budget, not only a generated-sequence-count cap.

The closest public PR is `vllm-project/vllm#45390`, which covers multiple DoS fixes including `GHSA-83mh-6mwq-3hg9` for `BatchChatCompletionRequest.messages`. That PR adds an outer bound to batch chat conversations, but its diff does not touch `vllm/entrypoints/openai/completion/protocol.py` or `vllm/entrypoints/openai/completion/serving.py`.

Prior local/private report families checked included pooling/rerank batch fanout, derender token-id postprocessing, explicit `truncation_side` tokenizer-limit bypass, Python disaggregated generate prompt-length bypass, and priority scheduling. Those reports differ by endpoint, attacker-controlled field, sink, and fix surface.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-87x5-vmc3-756j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73559
- https://github.com/vllm-project/vllm/pull/47845
- https://github.com/vllm-project/vllm/commit/675f4295cdfe0d870471c2b51bfeca3a68a9569e
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/releases/tag/v0.26.0
