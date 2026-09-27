# [M] JLSEC-2026-1162

## Summary
Severity: Medium
Advisory: JLSEC-2026-1162
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/JLSEC-2026-1162
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.1.0+0

## Details
HDF5 is a high-performance library and a file format specification that implements the HDF5 data model. If a file is corrupted such that an array datatype's size, the number of elements, and the element size  are not in agreement it can trigger an out of bounds read. The array datatype stores the full size of the datatype (`dt->shared->size`) separately from the number of elements (`dt->shared->u.array.nelem`) and the element size (`dt->shared->parent->shared->size`). If any one of these are corrupted so that they don't align with the others (element size * nelem = full size), it can lead to an out of bounds read. Depending on what is corrupted, it can alter the type of out of bounds read triggered. The vulnerability is present only in files that have been maliciously altered, as its generally not possible to independently alter the full size of the datatype, the element count and the element size. As such, this is only present if a malicious actor is altering files, and won't appear in regular usage.

## References
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-gh44-7wpq-622f
