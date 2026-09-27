# [M] JLSEC-2026-301

## Summary
Severity: Medium
Advisory: JLSEC-2026-301
Ecosystem: Julia
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-301
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 may attempt to dereference uninitialized values in `h5tools_str_sprint` in `tools/lib/h5tools_str.c` (called from `h5tools_dump_simple_data` in `tools/lib/h5tools_dump.c`).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
