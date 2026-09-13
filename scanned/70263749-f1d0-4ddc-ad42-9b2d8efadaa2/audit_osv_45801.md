# [H] JLSEC-2026-345

## Summary
Severity: High
Advisory: JLSEC-2026-345
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-345
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability, which was classified as problematic, was found in HDF5 1.14.6. Affected is the function `H5O__chunk_protect` of the file `/src/H5Ochunk.c`. The manipulation leads to heap-based buffer overflow. An attack has to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5573
- https://github.com/user-attachments/files/20623382/hdf5_crash_5.txt
- https://vuldb.com/?ctiid.314256
- https://vuldb.com/?id.314256
- https://vuldb.com/?submit.602326
