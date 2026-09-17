# [H] JLSEC-2026-300

## Summary
Severity: High
Advisory: JLSEC-2026-300
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-300
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 has a heap-based buffer over-read in `H5VM_memcpyvv` in H5VM.c (called from `H5D__compact_readvv` in H5Dcompact.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
