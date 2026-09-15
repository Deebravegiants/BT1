# [M] JLSEC-2026-1163

## Summary
Severity: Medium
Advisory: JLSEC-2026-1163
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/JLSEC-2026-1163
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.1.0+0

## Details
HDF5 is a high-performance library and a file format specification that implements the HDF5 data model. If `H5Iget_name` is invoked on a group id with `0` for the size parameter, it will underflow when trying to place a null terminator in the buffer. This can occur if `H5Iget_name` is invoked in a way where `size` can be forced to zero, and there is important data before the `name` buffer.

## References
- https://github.com/HDFGroup/hdf5/blob/develop/src/H5Gname.c#L474
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-5c6x-jmgf-f5vc
