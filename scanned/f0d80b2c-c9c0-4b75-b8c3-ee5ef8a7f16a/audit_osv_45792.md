# [M] JLSEC-2026-330

## Summary
Severity: Medium
Advisory: JLSEC-2026-330
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-330
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability was found in HDF5 up to 1.14.6. It has been rated as critical. Affected by this issue is the function `H5FL__blk_gc_list` of the file `src/H5FL.c`. The manipulation of the argument `H5FL_blk_head_t` leads to use after free. An attack has to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5376
- https://vuldb.com/?ctiid.301886
- https://vuldb.com/?id.301886
- https://vuldb.com/?submit.520404
