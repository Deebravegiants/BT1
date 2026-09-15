# [M] JLSEC-2026-348

## Summary
Severity: Medium
Advisory: JLSEC-2026-348
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-348
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability was found in HDF5 1.14.6 and classified as problematic. Affected by this issue is the function `H5C__flush_single_entry` of the file `src/H5Centry.c`. The manipulation leads to null pointer dereference. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5576
- https://github.com/user-attachments/files/20623475/hdf5_crash_8.txt
- https://vuldb.com/?ctiid.314330
- https://vuldb.com/?id.314330
- https://vuldb.com/?submit.602530
