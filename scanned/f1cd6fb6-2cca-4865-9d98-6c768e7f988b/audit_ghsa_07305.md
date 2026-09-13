# [H] vLLM has Remote DoS via Invalid Recovered Token Reinjection

## Summary
Severity: High
Advisory: GHSA-8wr5-jm2h-8r4f
CVE: CVE-2026-54234
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-8wr5-jm2h-8r4f
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.17.1 <0.24.0

## Details
## Summary

A frontend-legal multi-request speculative workload can make vLLM produce an out-of-vocabulary recovered token equal to `vocab_size`, convert that value to `-1` when choosing the next live token for a request, and then feed that `-1` back into the next drafter input ids. On Qwen3 GPTQ this reaches the worker-side drafting / attention path and crashes the engine with a GPU `device-side assert`.

The same issue is reachable through the public gRPC request surface by sending a specific overlapping `Generate` / `Abort` sequence.

## Impact

- A remote client that can send public gRPC generation requests can crash the
  shared vLLM engine worker
- The triggering request sequence aborts concurrent requests and prevents later
  requests from completing until the worker is restarted
- In shared deployments, this is a service-wide denial of service for other
  clients, not just a failure isolated to the attacking requests
- The failure is reproducible, so repeated request sequences can sustain the
  outage

## Affected version

- Confirmed on vLLM `0.17.1`
- Earlier and later versions have not been checked yet in this report

## Repro model

- Official Hugging Face repo:
  - [`Qwen/Qwen3-0.6B-GPTQ-Int8`](https://huggingface.co/Qwen/Qwen3-0.6B-GPTQ-Int8)
- Anyone wants to reproduce the bug with my PoC scripts should download `Qwen3-0.6B-GPTQ-Int8` first

## Trigger chain

1. A legal multi-request speculative workload keeps structured-output state,
   speculative decoding, overlap, and request cancellation active in the same
   live engine.
2. During rejection sampling, vLLM produces a recovered token equal to the
   model `vocab_size` boundary value.
3. That recovered token appears in position 0 of the sampled speculative row
   for a live request. The same row also contains trailing padding entries
   equal to `-1`, but those padding entries are not the key fault by
   themselves.
4. The next-token preparation step treats the position-0 recovered token as the
   real next token for that request and converts that out-of-vocabulary value
   to `-1`.
5. The drafter writes that converted `-1` back into the live next-step input-id
   row for the request.
6. The drafting / embedding / attention path later consumes that live invalid
   token and the worker crashes on GPU.

## Details

### Simple example

The important distinction is:

- trailing `-1` values in a speculative row can be ordinary padding
- the bug appears when the first live token for a request becomes
  `151936 == vocab_size`, and that live token is then converted into `-1`

In simplified form, the bad transition looks like this:

```text
sampled speculative row:
[151936, -1, -1, -1, ...]
```

At this point, the trailing `-1` values are only padding. The critical problem
is that the first position holds `151936`, which is out of vocabulary and is
being treated as the request's real next token.

Then vLLM prepares the next-token buffer:

```text
next_token_ids:
[-1, ...]
```

Finally, that converted `-1` is written back into the live model input ids:

```text
input_ids_after:
[-1, 0, 0, 0, ...]
```

The crash happens because the live next token became `-1` and was later consumed by the drafting / embedding / attention path, not merely because the speculative row contained padded `-1` entries.

### Trigger path in code

1. The workload is frontend-legal. The requests use normal `SamplingParams`
   features such as structured outputs, `stop`, `bad_words`, `min_tokens`, and
   streaming overlap. No malformed token-id list is required at the request
   boundary.
2. In speculative decoding, the rejection sampler can generate recovered tokens
   when drafted tokens are rejected.
   ```python
   # vllm/v1/sample/rejection_sampler.py
   def sample_recovered_tokens(...):
       recovered_token_ids = torch.empty_like(draft_token_ids)
       sample_recovered_tokens_kernel[(batch_size, max_spec_len)](...)
       return recovered_token_ids
   ```
   On the verified Qwen3 run, the recovered-token trace shows
   `recovered_token_ids[0] = 151936`, which is exactly `vocab_size` for this
   checkpoint.
3. The speculative proposer then prepares the next-token row from the sampled
   speculative row.
   ```python
   # vllm/v1/spec_decode/eagle.py
   def prepare_next_token_ids_padded(...):
       ...
       eagle_prepare_next_token_padded_kernel[grid](
           sampled_token_ids,
           discard_request_mask,
           backup_tokens_gpu,
           next_token_ids,
           valid_sampled_tokens_count,
           gpu_input_batch.vocab_size,
           ...
       )
       return next_token_ids, valid_sampled_tokens_count
   ```
   In the verified trace, this step receives a sampled row beginning with
   `151936`, followed by `-1` padding. The important point is that `151936`
   occupies the first live token position for the request. This step then
   produces `next_token_ids[0] = -1`, meaning the live next token for the
   request has been converted to `-1`.
4. The drafter then rotates the draft input ids and inserts those
   `next_token_ids` back into the live input-id buffer.
   ```python
   # vllm/v1/spec_decode/eagle.py
   def set_inputs_first_pass(...):
       ...
       self.input_ids[token_indices_to_sample] = next_token_ids
   ```
   In the verified trace, this produces `input_ids_after[0] = -1`.
5. The model-side embed path later consumes those input ids.
   ```python
   # vllm/model_executor/models/qwen2.py
   def embed_input_ids(self, input_ids: torch.Tensor) -> torch.Tensor:
       return self.embed_tokens(input_ids)
   ```
   In the verified trace, this is the first point where the converted `-1`
   becomes visible as a real model input. The bug is not merely that the
   sampled speculative row contained padding `-1`; the bug is that the live
   next token for the request became `-1` and was written back into input ids.
6. After that point, the visible sink depends on timing and backend state. On
   the attached Qwen3 reproducer, the engine commonly dies later in the
   drafting / attention path with `CUDA error: device-side assert triggered`,
   for example under `flash_attn_varlen_func(...)`.

### Local script breakdown

`repro_g4_recovered_minus1_local.py` is a standalone local reproducer.

- It reads the Qwen3 checkpoint path from `VLLM_POC_G4_MODEL` or the built-in
  `/path/to/qwen3` placeholder
- It creates `EngineCore` directly without any external helper dependency
- It submits one fixed multi-request workload that preserves the same overlap
  and speculative-decoding state needed for the bug
- It writes:
  - `request_payloads.json`
  - `repro_config.json`
  - `timeline.json`
  - `responses.json`
  - `error.txt`
  - `recovered_chain_trace.jsonl`
- `recovered_chain_trace.jsonl` is the key attribution artifact. It records the
  recovered-token chain directly from the standalone reproducer

### gRPC script breakdown

`repro_g4_recovered_minus1_grpc.py` is a standalone public gRPC reproducer.

- It reads the Qwen3 checkpoint path from `VLLM_POC_G4_MODEL` or the built-in
  `/path/to/qwen3` placeholder
- It starts a temporary `vllm.entrypoints.grpc_server` process
- It sends only public `Generate` and `Abort` RPCs
- It submits one fixed overlapping request sequence that preserves the same
  speculative-decoding state needed for the bug
- After the crash window, it sends one more public `Generate` probe request to
  confirm that later gRPC requests also fail after the worker dies
- It writes:
  - `request_payloads.json`
  - `timeline.json`
  - `server_command.json`
  - `responses.json`
  - `post_crash_probe.json`
  - `server.stdout.log`
  - `server.stderr.log`

## Observed result

Local repro typically ends with:

- a recovered-token trace showing:
  - `sample_recovered_tokens_return -> recovered_token_ids[0] = 151936`
  - `prepare_next_token_ids_padded -> next_token_ids[0] = -1`
  - `set_inputs_first_pass -> input_ids_after[0] = -1`
  - `embed_input_ids_out_of_range -> input_ids[0] = -1`
- `CUDA error: device-side assert triggered`
- a fatal engine-side failure

gRPC repro typically ends with:

- the triggering gRPC requests failing with
  `INTERNAL: EngineCore encountered an issue. See stack trace (above) for the root cause.`
- server logs showing the worker dies with
  `CUDA error: device-side assert triggered`
- a later public probe request also failing after the worker is dead

This demonstrates that the issue is reachable through the public gRPC request surface, not only through a local reproducer.

## Log snippets

### Local recovered-chain trace

```text
sample_recovered_tokens_return:
  recovered_token_ids = [151936, ...]
  vocab_size = 151936

prepare_next_token_ids_padded:
  sampled_token_ids_head = [[151936, -1, -1, ...], ...]
  next_token_ids = [-1, ...]

set_inputs_first_pass:
  input_ids_after = [-1, 0, 0, 0, ...]

embed_input_ids_out_of_range:
  input_ids = [-1, 0, 0, 0, ...]
```

### gRPC server log

```text
torch.AcceleratorError: CUDA error: device-side assert triggered
...
vllm.v1.engine.exceptions.EngineDeadError: EngineCore encountered an issue. See stack trace (above) for the root cause.
...
Error in Generate for request post_crash_probe
vllm.v1.engine.exceptions.EngineDeadError: EngineCore encountered an issue. See stack trace (above) for the root cause.
```

## Root cause

This is a speculative-decoding state-handling bug, not an invalid frontend token-id input bug.

The root cause is that a recovered speculative token can become equal to `vocab_size`, then be selected as the live next token for a request, then be converted to `-1`, and that converted `-1` is still written back into live drafter input ids and later consumed by the drafting / embedding / attention path.

For the Qwen3 checkpoint used here:

- `151936 == vocab_size`

This value should be described as the model `vocab_size` boundary value, not as a legal token id.

## Attachments

The attached bundle for this report should contain:

- `repro_g4_recovered_minus1_local.py`
- `repro_g4_recovered_minus1_grpc.py`

These two standalone scripts are sufficient to reproduce the issue and its public gRPC reachability.

## Fix

A fix for this vulnerability has been merged in: https://github.com/vllm-project/vllm/pull/44744

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-8wr5-jm2h-8r4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-54234
- https://github.com/vllm-project/vllm/pull/44744
- https://github.com/vllm-project/vllm/commit/8a5cf1ccd65e8ac7635c402c1ec0b08988bc26ca
- https://github.com/vllm-project/vllm
