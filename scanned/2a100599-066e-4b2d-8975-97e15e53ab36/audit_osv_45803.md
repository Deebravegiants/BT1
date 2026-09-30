# [H] JLSEC-2026-347

## Summary
Severity: High
Advisory: JLSEC-2026-347
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-347
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability has been found in HDF5 1.14.6 and classified as problematic. Affected by this vulnerability is the function `H5G__node_cmp3` of the file `src/H5Gnode.c`. The manipulation leads to stack-based buffer overflow. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5575
- https://github.com/user-attachments/files/20623442/hdf5_crash_7.txt
- https://vuldb.com/?ctiid.314329
- https://vuldb.com/?id.314329
- https://vuldb.com/?submit.602529
