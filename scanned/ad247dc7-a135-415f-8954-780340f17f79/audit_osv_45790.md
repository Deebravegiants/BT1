# [M] JLSEC-2026-329

## Summary
Severity: Medium
Advisory: JLSEC-2026-329
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-329
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability was found in HDF5 up to 1.14.6. It has been declared as problematic. Affected by this vulnerability is the function `H5O_msg_flush` of the file `src/H5Omessage.c`. The manipulation of the argument oh leads to heap-based buffer overflow. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5370
- https://vuldb.com/?ctiid.301885
- https://vuldb.com/?id.301885
- https://vuldb.com/?submit.519966
