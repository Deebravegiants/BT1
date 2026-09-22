# [M] JLSEC-2026-339

## Summary
Severity: Medium
Advisory: JLSEC-2026-339
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-339
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability classified as critical was found in HDF5 up to 1.14.6. Affected by this vulnerability is the function `H5C__reconstruct_cache_entry` of the file H5Cimage.c. The manipulation leads to heap-based buffer overflow. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5579
- https://github.com/user-attachments/files/20626503/reproduce.tar.gz
- https://vuldb.com/?ctiid.313273
- https://vuldb.com/?id.313273
- https://vuldb.com/?submit.592587
