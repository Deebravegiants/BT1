# [M] JLSEC-2026-1118

## Summary
Severity: Medium
Advisory: JLSEC-2026-1118
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1118
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
A flaw has been found in LibRaw up to 0.22.0. This affects the function `LibRaw::nikon_load_padded_packed_raw` of the file `src/decoders/decoders_libraw.cpp` of the component TIFF/NEF. Executing a manipulation of the argument `load_flags/raw_width` can lead to out-of-bounds read. It is possible to launch the attack remotely. The exploit has been published and may be used. Upgrading to version 0.22.1 mitigates this issue. This patch is called b8397cd45657b84e88bd1202528d1764265f185c. It is advisable to upgrade the affected component.

## References
- https://github.com/LibRaw/LibRaw/
- https://github.com/LibRaw/LibRaw/commit/b8397cd45657b84e88bd1202528d1764265f185c
- https://github.com/LibRaw/LibRaw/issues/795
- https://github.com/LibRaw/LibRaw/issues/795#issuecomment-4073769886
- https://github.com/LibRaw/LibRaw/releases/tag/0.22.1
- https://github.com/biniamf/pocs/tree/main/libraw_nikonpadded
- https://vuldb.com/submit/781223
- https://vuldb.com/vuln/354671
- https://vuldb.com/vuln/354671/cti
