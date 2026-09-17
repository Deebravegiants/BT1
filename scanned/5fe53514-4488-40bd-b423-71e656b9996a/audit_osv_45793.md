# [M] JLSEC-2026-332

## Summary
Severity: Medium
Advisory: JLSEC-2026-332
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-332
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
A vulnerability classified as problematic was found in HDF5 up to 1.14.6. This vulnerability affects the function `H5F__accum_free` of the file `src/H5Faccum.c`. The manipulation of the argument `overlap_size` leads to heap-based buffer overflow. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5380
- https://vuldb.com/?ctiid.301888
- https://vuldb.com/?id.301888
- https://vuldb.com/?submit.520899
