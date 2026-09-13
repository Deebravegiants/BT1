# [M] JLSEC-2026-1385

## Summary
Severity: Medium
Advisory: JLSEC-2026-1385
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1385
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.2.0+0

## Details
A double free vulnerability was discovered in the HDF5 library. Processing a crafted HDF5 file containing an oversized chunk size field via h5repack may cause the application to abort due to a double free.

## References
- https://github.com/HDFGroup/hdf5/issues/6124
- https://github.com/HDFGroup/hdf5/issues/6124
