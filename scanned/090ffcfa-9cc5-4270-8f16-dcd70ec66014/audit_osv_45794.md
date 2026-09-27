# [M] JLSEC-2026-334

## Summary
Severity: Medium
Advisory: JLSEC-2026-334
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-334
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability, which was classified as problematic, was found in HDF5 up to 1.14.6. This affects the function `H5HL__fl_deserialize` of the file `src/H5HLcache.c`. The manipulation of the argument `free_block` leads to heap-based buffer overflow. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5382
- https://vuldb.com/?ctiid.301899
- https://vuldb.com/?id.301899
- https://vuldb.com/?submit.521170
