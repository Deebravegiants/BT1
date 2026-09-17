# [H] JLSEC-2026-327

## Summary
Severity: High
Advisory: JLSEC-2026-327
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-327
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability has been found in HDF5 1.14.6 and classified as critical. This vulnerability affects the function `H5T__bit_copy` of the component Type Conversion Logic. The manipulation leads to heap-based buffer overflow. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. The vendor plans to fix this issue in an upcoming release.

## References
- https://github.com/madao123123/crash_report/blob/main/hdf5_poc/hdf5_poc3.md
- https://vuldb.com/?ctiid.299722
- https://vuldb.com/?id.299722
- https://vuldb.com/?submit.514532
