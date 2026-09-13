# [H] JLSEC-2026-318

## Summary
Severity: High
Advisory: JLSEC-2026-318
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-318
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in `H5VM_array_fill` in H5VM.c (called from `H5S_select_elements` in H5Spoint.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
