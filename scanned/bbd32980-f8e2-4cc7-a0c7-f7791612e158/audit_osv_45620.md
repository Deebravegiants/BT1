# [M] JLSEC-2026-1384

## Summary
Severity: Medium
Advisory: JLSEC-2026-1384
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:H/SC:N/SI:L/SA:H/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/JLSEC-2026-1384
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.2.0+0

## Details
Heap-based buffer overflow in the SOHM list-index deserialization code in HDF5 through 2.1.1 on all platforms allows attackers to cause a denial of service (crash) via a crafted HDF5 file whose shared-message list index declares a `num_messages` count exceeding `list_max`, triggering out-of-bounds heap reads and writes in `H5SM__cache_list_deserialize` and `H5SM__cache_list_verify_chksum`.

## References
- https://github.com/HDFGroup/hdf5/issues/6501
