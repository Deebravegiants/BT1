# [M] JLSEC-2026-335

## Summary
Severity: Medium
Advisory: JLSEC-2026-335
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-335
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability has been found in HDF5 up to 1.14.6 and classified as problematic. This vulnerability affects the function `H5MM_realloc` of the file `src/H5MM.c`. The manipulation of the argument mem leads to double free. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5383
- https://vuldb.com/?ctiid.301900
- https://vuldb.com/?id.301900
- https://vuldb.com/?submit.521193
