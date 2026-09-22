# [M] JLSEC-2026-336

## Summary
Severity: Medium
Advisory: JLSEC-2026-336
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-336
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability was found in HDF5 up to 1.14.6 and classified as problematic. This issue affects the function `H5O__cache_chk_serialize` of the file `src/H5Ocache.c`. The manipulation leads to null pointer dereference. An attack has to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5384
- https://vuldb.com/?ctiid.301901
- https://vuldb.com/?id.301901
- https://vuldb.com/?submit.521246
