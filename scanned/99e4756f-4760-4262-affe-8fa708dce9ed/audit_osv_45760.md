# [H] JLSEC-2026-294

## Summary
Severity: High
Advisory: JLSEC-2026-294
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-294
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 through 1.14.3 contains a heap buffer overflow in `H5A__attr_release_table`, resulting in the corruption of the instruction pointer and causing denial of service or potential code execution.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
