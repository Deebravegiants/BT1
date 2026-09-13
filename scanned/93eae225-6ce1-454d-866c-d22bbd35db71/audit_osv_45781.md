# [C] JLSEC-2026-317

## Summary
Severity: Critical
Advisory: JLSEC-2026-317
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-317
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 contains a out-of-bounds read operation in `H5FL_arr_malloc` in H5FL.c (called from `H5S_set_extent_simple` in H5S.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
