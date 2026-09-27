# [H] JLSEC-2026-308

## Summary
Severity: High
Advisory: JLSEC-2026-308
Ecosystem: Julia
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-308
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer over-read in the function `H5HL__fl_deserialize` in H5HLcache.c, a different vulnerability than CVE-2024-32612.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
