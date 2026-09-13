# [H] JLSEC-2026-319

## Summary
Severity: High
Advisory: JLSEC-2026-319
Ecosystem: Julia
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-319
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in `H5T__ref_mem_setnull` in H5Tref.c (called from `H5T__conv_ref` in H5Tconv.c), resulting in the corruption of the instruction pointer.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
