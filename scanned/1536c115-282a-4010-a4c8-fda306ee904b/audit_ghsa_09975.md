# [M] vLLM: Denial of Service via Unbounded Frame Count in video/jpeg Base64 Processing

## Summary
Severity: Medium
Advisory: GHSA-pq5c-rjhq-qp7p
CVE: CVE-2026-34755
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-pq5c-rjhq-qp7p
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.7.0 <0.19.0

## Details
## Summary

The `VideoMediaIO.load_base64()` method at `vllm/multimodal/media/video.py:51-62` splits `video/jpeg` data URLs by comma to extract individual JPEG frames, but does not enforce a frame count limit. The `num_frames` parameter (default: 32), which is enforced by the `load_bytes()` code path at line 47-48, is completely bypassed in the `video/jpeg` base64 path. An attacker can send a single API request containing thousands of comma-separated base64-encoded JPEG frames, causing the server to decode all frames into memory and crash with OOM.

## Details

### Vulnerable code

```python
# video.py:51-62
def load_base64(self, media_type: str, data: str) -> tuple[npt.NDArray, dict[str, Any]]:
    if media_type.lower() == "video/jpeg":
        load_frame = partial(self.image_io.load_base64, "image/jpeg")
        return np.stack(
            [np.asarray(load_frame(frame_data)) for frame_data in data.split(",")]
            #                                                       ^^^^^^^^^^
            # Unbounded split — no frame count limit
        ), {}
    return self.load_bytes(base64.b64decode(data))
```

The `load_bytes()` path (line 47-48) properly delegates to a video loader that respects `self.num_frames` (default 32). The `load_base64("video/jpeg", ...)` path bypasses this limit entirely — `data.split(",")` produces an unbounded list and every frame is decoded into a numpy array.

### video/jpeg is part of vLLM's public API

`video/jpeg` is a vLLM-specific MIME type, not IANA-registered. However it is part of the public API surface:

- `encode_video_url()` at `vllm/multimodal/utils.py:96-108` generates `data:video/jpeg;base64,...` URLs
- Official test suites at `tests/entrypoints/openai/test_video.py:62` and `tests/entrypoints/test_chat_utils.py:153` both use this format

### Memory amplification

Each JPEG frame decodes to a full numpy array. For 640x480 RGB images, each frame is ~921 KB decoded. 5000 frames = ~4.6 GB. `np.stack()` then creates an additional copy. The compressed JPEG payload is small (~100 KB for 5000 frames) but decompresses to gigabytes.

### Data flow

```
POST /v1/chat/completions
  → chat_utils.py:1434   video_url type → mm_parser.parse_video()
  → chat_utils.py:872    parse_video() → self._connector.fetch_video()
  → connector.py:295     fetch_video() → load_from_url(url, self.video_io)
  → connector.py:91      _load_data_url(): url_spec.path.split(",", 1)
                          → media_type = "video/jpeg"
                          → data = "<frame1>,<frame2>,...,<frame10000>"
  → connector.py:100     media_io.load_base64("video/jpeg", data)
  → video.py:54          data.split(",")  ← UNBOUNDED
  → video.py:55-57       all frames decoded into numpy arrays
  → video.py:56          np.stack([...])  ← massive combined array → OOM
```

`connector.py:91` uses `split(",", 1)` which splits on only the first comma. All remaining commas stay in `data` and are later split by `video.py:54`.

### Comparison with existing protections

| Code Path | Frame Limit | File |
|-----------|-------------|------|
| `load_bytes()` (binary video) | Yes — `num_frames` (default 32) | video.py:46-49 |
| `load_base64("video/jpeg", ...)` | No — unlimited `data.split(",")` | video.py:51-62 |

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-pq5c-rjhq-qp7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-34755
- https://github.com/vllm-project/vllm/pull/38636
- https://github.com/vllm-project/vllm/commit/58ee61422169ce17e08248f8efa1e9df434fe395
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34755.json
- https://github.com/vllm-project/vllm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-144.yaml
- https://bugzilla.redhat.com/show_bug.cgi?id=2455403
- https://access.redhat.com/security/cve/CVE-2026-34755
- https://access.redhat.com/errata/RHSA-2026:59151
- https://access.redhat.com/errata/RHSA-2026:59144
- https://access.redhat.com/errata/RHSA-2026:57390
- https://access.redhat.com/errata/RHSA-2026:57389
- https://access.redhat.com/errata/RHSA-2026:57387
- https://access.redhat.com/errata/RHSA-2026:57380
- https://access.redhat.com/errata/RHSA-2026:36006
- https://access.redhat.com/errata/RHSA-2026:36005
