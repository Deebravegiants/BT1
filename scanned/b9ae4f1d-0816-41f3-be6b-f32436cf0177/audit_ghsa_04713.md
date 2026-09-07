# [M] vLLM: incomplete CVE-2026-22778 fix leaks PIL repr addresses via Anthropic router

## Summary
Severity: Medium
Advisory: GHSA-hgg8-fqqc-vfmw
CVE: CVE-2026-54236
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-hgg8-fqqc-vfmw
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.24.0

## Details
# vLLM: incomplete CVE-2026-22778 fix leaks PIL repr addresses via the Anthropic API router

**Researcher:** Kai Aizen — SnailSploit (@SnailSploit), Adversarial & Offensive Security Research
**Severity:** CVSS 3.1 5.3 (Medium)  `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`
**Target:** https://github.com/vllm-project/vllm

---

## Summary

The fix for CVE-2026-22778 / GHSA-4r2x-xpjr-7cvv (PRs #31987 and #32319) introduced `sanitize_message` and applied it at four FastAPI exception-handling sites in the OpenAI router. The sanitizer strips object-repr memory addresses (`<_io.BytesIO object at 0x7a95e299e750>` → `<_io.BytesIO object>`) before error messages reach the client, defeating the ASLR-bypass primitive that CVE-2026-22778 chained with a libopenjp2 heap overflow for RCE.

The fix is incomplete: response paths added to vLLM at or after the same time as the fix continue to echo `str(exc)` directly to clients without `sanitize_message`. The original Stage 1 primitive — sending malformed image bytes so PIL raises `UnidentifiedImageError` whose message contains the BytesIO object repr — reaches all of them unmodified and leaks the heap address verbatim in the response body.

All five lines below are present in `main` HEAD (`771e1e48b`, 2026-05-26).

## Affected sites

Current `main` HEAD (`771e1e48b`, 2026-05-26):

| # | File | Line | Code |
|---|---|---|---|
| 1 | `vllm/entrypoints/anthropic/api_router.py` | 78 | `message=str(e),` (inside `POST /v1/messages` exception handler) |
| 2 | `vllm/entrypoints/anthropic/api_router.py` | 124 | `message=str(e),` (inside `POST /v1/messages/count_tokens`) |
| 3 | `vllm/entrypoints/anthropic/serving.py` | 808 | `error=AnthropicError(type="internal_error", message=str(e)),` (SSE streaming converter) |
| 4 | `vllm/entrypoints/speech_to_text/realtime/connection.py` | 75 | `await self.send_error(str(e), "processing_error")` (WebSocket event loop) |
| 5 | `vllm/entrypoints/speech_to_text/realtime/connection.py` | 265 | `await self.send_error(str(e), "processing_error")` (WebSocket generation loop) |

## Why the global exception handler does not save these paths

`api_server.py` registers a catch-all `app.exception_handler(Exception)(exception_handler)` at line 262, and that handler calls `create_error_response(exc)` which DOES apply `sanitize_message`. However, FastAPI exception handlers fire only on **unhandled** exceptions that propagate out of a route function.

All affected HTTP paths catch `Exception` *inside* the route coroutine and construct the response themselves:

```python
# vllm/entrypoints/anthropic/api_router.py:71-81 (POST /v1/messages)
try:
    generator = await handler.create_messages(request, raw_request)
except Exception as e:
    logger.exception("Error in create_messages: %s", e)
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        content=AnthropicErrorResponse(
            error=AnthropicError(
                type="internal_error",
                message=str(e),       # <-- unsanitized
            )
        ).model_dump(),
    )
```

Because the exception is caught and a `JSONResponse` is returned in-route, every registered FastAPI exception handler — including the sanitizing global one — is bypassed. The WebSocket path bypasses it for a different reason: WebSocket frames don't traverse FastAPI's HTTP exception handler chain at all.

## Reachability — the same primitive as the parent CVE

The Anthropic Messages API accepts image content parts in the request body (`type: "image"` with base64 `source.data` or `type: "image_url"`). Image bytes are passed to the same multimodal loader used by the OpenAI router. Malformed bytes cause `PIL.Image.open` to raise:

```
UnidentifiedImageError: cannot identify image file <_io.BytesIO object at 0x7a95e299e750>
```

The exception propagates up through `handler.create_messages` into the `except Exception as e:` at `api_router.py:75`. `str(e)` returns the exception message verbatim, including the address. The address ends up in the `error.message` field of the JSON response body returned to the attacker. ASLR entropy on the affected process drops from ~4 billion to ~8 candidates, identically to CVE-2026-22778 Stage 1.

The same primitive is reachable on `POST /v1/messages/count_tokens` (route #2), inside the SSE streaming converter when an exception is raised mid-stream (route #3), and over the realtime speech-to-text WebSocket when audio decoder or generation paths raise an exception containing any object repr (routes #4, #5).

## Chronology — these are scope misses, not legacy code

- **2026-01-09:** PR #31987 (`aa125ecf0`) introduces `sanitize_message` and applies it to OpenAI router HTTP exception handlers.
- **2026-01-15** (six days later): PR #32369 (`4c1c501a7`) adds `vllm/entrypoints/anthropic/api_router.py` containing line 78's `message=str(e)`. The fix was not applied to the new router.
- **2026-03-02** (~two months later): PR #35588 (`9a87b0578`) adds the Anthropic `count_tokens` endpoint, replicating the same `message=str(e)` pattern at line 124.
- **2026-05-12** (~four months later): PR #42370 (`d37e25ffb`) consolidates speech-to-text entrypoints and the realtime WebSocket uses `send_error(str(e), ...)` for both error paths.
- **2026-05-26:** current `main` HEAD, all five lines still present.

## CVSS v3.1

`AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` — Base 5.3 (MEDIUM)

The parent CVE-2026-22778 was 9.8 (CRITICAL) because it chained the Stage 1 leak with a Stage 2 libopenjp2 heap overflow. Stage 2 is patched in OpenCV ≥ 4.13.0 (PR #32668 bumped the requirement), so Stage 1 alone here is a partial ASLR-bypass info-disclosure primitive rather than a complete RCE. Deployments that ship vLLM alongside an older OpenCV/libopenjp2 (system OpenCV on long-LTS distros, custom Docker images, downstream rebuilds) re-enable the full chain via the affected endpoints.

## CWE

CWE-532 (Insertion of Sensitive Information into Log File / Error Message). Same CWE assigned to the parent CVE-2026-22778.

## Remediation

### 1. Apply `sanitize_message` symmetrically to the five sites

```python
# vllm/entrypoints/anthropic/api_router.py — add at top:
from vllm.entrypoints.utils import sanitize_message

# Line 78 (POST /v1/messages) and Line 124 (count_tokens):
message=sanitize_message(str(e)),
```

```python
# vllm/entrypoints/anthropic/serving.py — add at top:
from vllm.entrypoints.utils import sanitize_message

# Line 808:
error=AnthropicError(type="internal_error", message=sanitize_message(str(e))),
```

```python
# vllm/entrypoints/speech_to_text/realtime/connection.py — add at top:
from vllm.entrypoints.utils import sanitize_message

# Lines 75 and 265:
await self.send_error(sanitize_message(str(e)), "processing_error")
```

### 2. Tighten the regex (defense in depth)

The current regex `r" at 0x[0-9a-f]+>"` is narrow — it only matches the exact CPython builtin object-repr suffix in lowercase hex with a trailing `>`. Future Python versions, C extensions, or custom `__repr__` methods could produce non-matching formats that re-enable the leak:

```python
# vllm/entrypoints/utils.py
def sanitize_message(message: str) -> str:
    # Strip any standalone hex address; downstream observers don't need them.
    return re.sub(r"\b0x[0-9a-fA-F]{6,}\b", "0x?", message)
```

### 3. Future-proofing: consider a response middleware

Both the route-local exception handling pattern (Anthropic router) and the WebSocket path bypass FastAPI's exception handler chain. A response-level middleware that always invokes `sanitize_message` on outgoing error bodies would prevent this class of regression entirely.

## Affected versions

- All vLLM versions containing `vllm/entrypoints/anthropic/api_router.py` (introduced 2026-01-15 in PR #32369).
- All vLLM versions containing `vllm/entrypoints/speech_to_text/realtime/connection.py` (introduced 2026-05-12 in PR #42370).
- Confirmed present in `main` HEAD `771e1e48b` (2026-05-26).

## References

- Parent advisory: https://github.com/vllm-project/vllm/security/advisories/GHSA-4r2x-xpjr-7cvv (CVE-2026-22778)
- Fix PRs to model the patch on: #31987, #32319, #32668
- `vllm/entrypoints/utils.py:sanitize_message`: https://github.com/vllm-project/vllm/blob/771e1e48b/vllm/entrypoints/utils.py#L323-L326
- `vllm/entrypoints/anthropic/api_router.py` leak site: https://github.com/vllm-project/vllm/blob/771e1e48b/vllm/entrypoints/anthropic/api_router.py#L78

## Steps to reproduce

1. Clone the target: `git clone --depth 1 https://github.com/vllm-project/vllm`
2. Run the proof of concept (`PoC.py`) against the cloned source.
3. Observe the result shown under *Verified result* below.

## Credit

Kai Aizen — SnailSploit (@SnailSploit). Adversarial & Offensive Security Research.

## Fix

A fix for this vulnerability was added here: https://github.com/vllm-project/vllm/pull/45119

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-hgg8-fqqc-vfmw
- https://nvd.nist.gov/vuln/detail/CVE-2026-54236
- https://github.com/vllm-project/vllm/pull/45119
- https://github.com/vllm-project/vllm/commit/94923629729381d7f7c9efde72071a2441f7fd82
- https://github.com/advisories/GHSA-hgg8-fqqc-vfmw
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-3408.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
