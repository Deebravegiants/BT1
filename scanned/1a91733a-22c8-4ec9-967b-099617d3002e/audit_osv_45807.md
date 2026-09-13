# [M] JLSEC-2026-350

## Summary
Severity: Medium
Advisory: JLSEC-2026-350
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-350
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability, which was classified as problematic, has been found in HDF5 1.14.6. This issue affects the function `H5FL__malloc` of the file `src/H5FL.c`. The manipulation leads to memory leak. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5578
- https://github.com/user-attachments/files/20623530/hdf5_crash_10.txt
- https://vuldb.com/?ctiid.314903
- https://vuldb.com/?id.314903
- https://vuldb.com/?submit.602537
