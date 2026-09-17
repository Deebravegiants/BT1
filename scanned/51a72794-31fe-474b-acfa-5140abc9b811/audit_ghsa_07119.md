# [M] vLLM: Speech-to-text upload size limit is enforced after full UploadFile read

## Summary
Severity: Medium
Advisory: GHSA-v82g-2437-67m2
CVE: CVE-2026-55646
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-v82g-2437-67m2
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.22.0 <0.24.0

## Details
## Summary

Current-head vLLM documents `VLLM_MAX_AUDIO_CLIP_FILESIZE_MB` as the maximum audio file size accepted by the speech-to-text APIs. The default is 25 MB. `vllm/envs.py` also describes files larger than this value as rejected.

The `/v1/audio/transcriptions` and `/v1/audio/translations` routes call `await request.file.read()` before vLLM checks that limit. In FastAPI and Starlette, `UploadFile.read()` returns bytes from the uploaded file object; when called without a size argument, the route materializes the remaining file contents. vLLM then performs the compressed file-size check later in `_preprocess_speech_to_text()` against the already-created `bytes` object.

As a result, the documented compressed audio file-size limit does not bound the memory allocated by vLLM endpoint code before validation. An oversized multipart upload can cause vLLM to allocate memory proportional to the uploaded file size before rejecting the request as too large.

This is distinct from `GHSA-6pr9-rp53-2pmc`, which covered decoded PCM expansion after compressed input was accepted. This report covers compressed upload materialization before compressed-size validation.

## Technical Details

The upload routes perform an unbounded read before vLLM checks the documented compressed audio file-size limit:

- `vllm/entrypoints/speech_to_text/transcription/api_router.py`: `audio_data = await request.file.read()`
- `vllm/entrypoints/speech_to_text/translation/api_router.py`: `audio_data = await request.file.read()`
- `vllm/entrypoints/speech_to_text/base/serving.py` later checks: `if len(audio_data) / 1024**2 > self.max_audio_filesize_mb`

There is no route-level check of `request.file.size`, `Content-Length`, a bounded `read(max_bytes + 1)`, or a streaming copy that stops at the configured limit before the full file is materialized.

This does not appear to be intended behavior. vLLM's security guide treats request-controlled resource use as a security boundary: for example, requests that exceed `VLLM_MAX_N_SEQUENCES` are rejected before reaching the engine. The speech-to-text upload limit is documented in the same spirit as an API enforced limit, but the first vLLM check happens after the over-limit upload has already been copied into a `bytes` object.

## Impact

Attack requirements:

- the deployment exposes `/v1/audio/transcriptions` or `/v1/audio/translations`;
- a speech-to-text capable model/task is configured; and
- the caller can submit requests to the endpoint, including any API key the deployment requires.

An API caller who meets those requirements can send an oversized audio file. vLLM reads the full uploaded file into memory before applying the configured compressed audio file-size limit. This can create memory pressure or, depending on process/container limits and concurrency, terminate the process before the request is rejected.

Suggested severity: Moderate, `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H` (`6.5`), CWE-770/CWE-400.

The impact is availability-only. This is not a claim of code execution, data access, cross-tenant data exposure, parser-level multipart memory exhaustion, or persistence after process restart. Deployment body-size limits at a reverse proxy or ASGI layer can mitigate the issue before vLLM sees the request, but vLLM's own documented file-size limit does not currently provide that memory boundary.

## Suggested Fix

Enforce the compressed audio upload limit before the unbounded read:

- Check reliable upload size metadata before reading when available.
- Read at most `max_bytes + 1` bytes in chunks as a defense-in-depth guard against missing or unreliable metadata.
- Share the helper between transcription and translation routes.
- Add regression tests that prove an over-limit `UploadFile` is rejected without calling an unbounded `read()`.

The important property is that over-limit compressed uploads are rejected before vLLM allocates the full uploaded file as `bytes`.

## Resources

- vLLM security policy: `https://github.com/vllm-project/vllm/security/policy`
- vLLM speech-to-text docs: `https://docs.vllm.ai/en/latest/serving/online_serving/speech_to_text/`
- vLLM security guide, request parameter resource limits: `https://docs.vllm.ai/en/latest/usage/security/`
- vLLM vulnerability management docs: `https://docs.vllm.ai/en/latest/contributing/vulnerability_management/`
- FastAPI file uploads: `https://fastapi.tiangolo.com/reference/uploadfile/`
- Starlette uploaded files: `https://www.starlette.io/requests/`
- Adjacent published audio advisory: `https://github.com/vllm-project/vllm/security/advisories/GHSA-6pr9-rp53-2pmc`
- Request-parameter resource DoS precedent: `https://github.com/vllm-project/vllm/security/advisories/GHSA-3mwp-wvh9-7528`

## Appendix: Affected Version

Validated against current head:

- commit: `1033ffac2eccf986fdd880f4dee64ca3b22c63c9`
- described version: `v0.22.1rc0-491-g1033ffac2e`

Known affected range: current head. It has not been determined the introducing commit or release range.

## Appendix: Proof Of Vulnerability

The attached proof is a non-destructive static probe. It does not upload a large file or contact a running vLLM server:

```bash
python3 attached-evidence/poc/audio_upload_size_precheck_probe.py
```

Observed result:

```json
{
  "pov": "this report",
  "validated": true,
  "default_limit_mb": 25,
  "documented_api_limit": true,
  "routes": {
    "transcription_route": {
      "unbounded_upload_read": true,
      "early_size_guard_before_read": false,
      "chunked_bounded_read": false
    },
    "translation_route": {
      "unbounded_upload_read": true,
      "early_size_guard_before_read": false,
      "chunked_bounded_read": false
    }
  },
  "late_size_check": {
    "present": true
  }
}
```

Expected behavior: vLLM rejects over-limit audio files before materializing the entire upload into memory in vLLM endpoint code.

Actual behavior: the route materializes the upload into memory first, and only then does vLLM reject the request as exceeding `VLLM_MAX_AUDIO_CLIP_FILESIZE_MB`.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-v82g-2437-67m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-55646
- https://github.com/vllm-project/vllm/pull/45510
- https://github.com/vllm-project/vllm/commit/b997071ec493765abbed990c65843ed05e4708a8
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2305.yaml
- https://github.com/vllm-project/vllm
