# [H] JLSEC-2026-312

## Summary
Severity: High
Advisory: JLSEC-2026-312
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-312
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer over-read caused by the unsafe use of strdup in `H5MM_xstrdup` in H5MM.c (called from `H5G__ent_to_link` in H5Glink.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
