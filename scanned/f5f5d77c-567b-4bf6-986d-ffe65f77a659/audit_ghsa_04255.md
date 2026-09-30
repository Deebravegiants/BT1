# [M] vLLM: OOM Denial of Service via Audio Decompression Bomb

## Summary
Severity: Medium
Advisory: GHSA-6pr9-rp53-2pmc
CVE: CVE-2026-54233
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-6pr9-rp53-2pmc
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.24.0

## Details
### Summary
vLLM's `/v1/audio/transcriptions` endpoint limits compressed upload size but not decoded PCM output. A 25MB OPUS file expands to ~14.9GB of float32 PCM at decode time. Tested on vLLM v0.19.0.

### Details
`SpeechToTextProcessor` rejects uploads over `VLLM_MAX_AUDIO_CLIP_FILESIZE_MB` (default 25MB) based on compressed byte length, but the audio decoder in `audio.py` accumulates all decoded frames into memory with no size limit before returning:

```python
# speech_to_text.py L184-189
if len(audio_data) / 1024 ** 2 > self.max_audio_filesize_mb:
    raise VLLMValidationError(...)
y, sr = load_audio(buf, sr=self.asr_config.sample_rate)  # decoded size unchecked

# audio.py L77-107
chunks: list[npt.NDArray] = []
for frame in container.decode(stream):
    chunks.append(frame.to_ndarray())
audio = np.concatenate(chunks, axis=-1).astype(np.float32)  # single contiguous allocation
```

A 25MB OPUS file at 6kbps encodes ~8.7 hours of audio. Decoding produces ~5.7GB of float32 PCM (232x amplification), and `np.concatenate` then allocates a second contiguous array, bringing peak RSS to ~14.9GB from a single request. `SpeechToTextConfig.max_audio_clip_s` (default 30s) applies only after the full decode and does not prevent the allocation.

### Impact
An unauthenticated attacker can exhaust server memory with a small number of concurrent requests, each a valid upload within the documented size limit. Severity was assessed with reference to prior OOM vulnerability reports in vLLM.

### Fix

A fix for this vulnerability was merged here: https://github.com/vllm-project/vllm/pull/44970

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-6pr9-rp53-2pmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54233
- https://github.com/vllm-project/vllm/pull/44970
- https://github.com/vllm-project/vllm/commit/1b1359c33269446f13c05da9a90c25174cbea590
- https://github.com/advisories/GHSA-6pr9-rp53-2pmc
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-3404.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/releases/tag/v0.23.1rc0
- https://pypi.org/project/vllm
