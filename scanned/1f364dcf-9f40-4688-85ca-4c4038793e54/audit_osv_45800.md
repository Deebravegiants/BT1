# [H] JLSEC-2026-341

## Summary
Severity: High
Advisory: JLSEC-2026-341
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-341
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability has been found in HDF5 up to 1.14.6 and classified as critical. This vulnerability affects the function `H5F_addr_decode_len` of the file `/hdf5/src/H5Fint.c`. The manipulation leads to heap-based buffer overflow. An attack has to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5581
- https://github.com/user-attachments/files/20626851/reproduce.tar.gz
- https://vuldb.com/?ctiid.313636
- https://vuldb.com/?id.313636
- https://vuldb.com/?submit.592589
