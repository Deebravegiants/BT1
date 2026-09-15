# [M] JLSEC-2026-302

## Summary
Severity: Medium
Advisory: JLSEC-2026-302
Ecosystem: Julia
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-302
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 has a SEGV in `H5A__close` in H5Aint.c, resulting in the corruption of the instruction pointer.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
