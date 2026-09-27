# [M] JLSEC-2026-351

## Summary
Severity: Medium
Advisory: JLSEC-2026-351
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-351
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability, which was classified as problematic, was found in HDF5 1.14.6. Affected is the function `H5FS__sect_link_size` of the file `src/H5FSsection.c`. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5550
- https://github.com/user-attachments/files/20438481/hdf5_crash_2.txt
- https://vuldb.com/?ctiid.314904
- https://vuldb.com/?id.314904
- https://vuldb.com/?submit.602538
