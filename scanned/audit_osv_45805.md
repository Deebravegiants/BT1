# [M] JLSEC-2026-349

## Summary
Severity: Medium
Advisory: JLSEC-2026-349
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-349
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability classified as problematic was found in HDF5 1.14.6. This vulnerability affects the function `H5FS__sinfo_serialize_node_cb` of the file `src/H5FScache.c`. The manipulation leads to heap-based buffer overflow. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5577
- https://github.com/user-attachments/files/20623499/hdf5_crash_9.txt
- https://vuldb.com/?ctiid.314902
- https://vuldb.com/?id.314902
- https://vuldb.com/?submit.602536
