# [H] JLSEC-2026-346

## Summary
Severity: High
Advisory: JLSEC-2026-346
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-346
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability, which was classified as problematic, was found in HDF5 1.14.6. Affected is the function `H5FL__reg_gc_list` of the file `src/H5FL.c`. The manipulation leads to use after free. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5574
- https://github.com/user-attachments/files/20623417/hdf5_crash_6.txt
- https://vuldb.com/?ctiid.314328
- https://vuldb.com/?id.314328
- https://vuldb.com/?submit.602528
