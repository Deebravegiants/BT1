# [H] Pillow JPEG2000 tiled decode retains a growing scratch buffer and can be used for denial of service

## Summary
Severity: High
Advisory: GHSA-vjc4-5qp5-m44j
CVE: CVE-2026-59204
CWE: CWE-770, CWE-789
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-vjc4-5qp5-m44j
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=8.2.0 <12.3.0

## Details
### Summary
`src/libImaging/Jpeg2KDecode.c:853` accumulates `total_component_width` across every tile in a JPEG2000 image instead of recomputing it per tile. That accumulated value is then used in the `tile_bytes` calculation at `src/libImaging/Jpeg2KDecode.c:868`, which can make the decoder grow `state->buffer` via `realloc` at `src/libImaging/Jpeg2KDecode.c:876` up to roughly one full image's decompressed size even when each tile is small. A crafted tiled JPEG2000 file can therefore force substantially higher transient memory usage and trigger out-of-memory failures during decoding. Based on current evidence, the supported impact is denial of service, not memory corruption.

### Details
- Location: `src/libImaging/Jpeg2KDecode.c:853`
- Root cause: `total_component_width` is initialized only once before the tile loop and keeps growing across tiles. It is then used to derive `tile_bytes`, so later tiles are treated as if they had the combined component width of all earlier tiles.
- Dangerous operation: `tile_bytes` is promoted into `tile_info.data_size`, then `state->buffer` is grown with `realloc` at `src/libImaging/Jpeg2KDecode.c:876`.
- Reachability: any attacker-controlled JPEG2000 image with many tiles reaches this path during normal `Image.open(...).load()` decoding.


### PoC
The attached helper script and testcase were used:
[exercise_j2k_tile_realloc.zip](https://github.com/user-attachments/files/28099912/exercise_j2k_tile_realloc.zip)


Generate the testcase:

```bash
pythonexercise_j2k_tile_realloc.py make poc_3664_rgba_tile1832.jp2 \
  --size 3664 --tile 1832
```

Expected geometry from the helper:

- image size: `3664 x 3664`
- mode: `RGBA`
- tile size: `1832 x 1832` (`2x2` tiles)
- `image_bytes=53699584`
- uncapped RSS observed:
  - vulnerable build: `maxrss_kb=180264`
  - fixed comparison build: `maxrss_kb=138404`

Load it with the current vulnerable build:

```bash
python exercise_j2k_tile_realloc.py load poc_3664_rgba_tile1832.jp2
```

Load it again under a 160 MB address-space cap:

```bash
python exercise_j2k_tile_realloc.py load poc_3664_rgba_tile1832.jp2 --limit-mb 160
```

### Impact
Conservative impact: denial of service through memory exhaustion during JPEG2000 decoding.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-vjc4-5qp5-m44j
- https://nvd.nist.gov/vuln/detail/CVE-2026-59204
- https://github.com/python-pillow/Pillow/pull/9704
- https://github.com/python-pillow/Pillow/commit/13ada41172142f2fd9f0906f615a00ea623a11ca
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.3.0
