# [M] JLSEC-2026-340

## Summary
Severity: Medium
Advisory: JLSEC-2026-340
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-340
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability, which was classified as critical, has been found in HDF5 up to 1.14.6. Affected by this issue is the function `H5FS__sect_find_node` of the file H5FSsection.c. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5580
- https://github.com/user-attachments/files/20626642/reproduce.tar.gz
- https://vuldb.com/?ctiid.313274
- https://vuldb.com/?id.313274
- https://vuldb.com/?submit.592588
