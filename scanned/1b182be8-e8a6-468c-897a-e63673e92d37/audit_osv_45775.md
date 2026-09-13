# [C] JLSEC-2026-310

## Summary
Severity: Critical
Advisory: JLSEC-2026-310
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-310
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in `H5Z__nbit_decompress_one_byte` in H5Znbit.c, caused by the earlier use of an initialized pointer.

## References
- https://github.com/HDFGroup/cve_hdf5/blob/main/CVE_list.md
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
