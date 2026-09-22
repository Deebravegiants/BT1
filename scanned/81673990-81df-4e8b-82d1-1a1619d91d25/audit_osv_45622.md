# [M] JLSEC-2026-1386

## Summary
Severity: Medium
Advisory: JLSEC-2026-1386
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1386
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.1.2+0

## Details
HDF5 contains a NULL pointer dereference vulnerability. Processing a crafted HDF5 file containing an attribute with an invalid variable-length datatype type field may cause the application to crash when the attribute is read.

## References
- https://github.com/HDFGroup/hdf5/commit/3fa6ed6e9dfeebbc784e21d8c48e31e35a8042bc
