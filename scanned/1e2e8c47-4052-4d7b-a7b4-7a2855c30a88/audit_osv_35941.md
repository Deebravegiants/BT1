# [M] NULL Pointer Dereference in HDF5 via Invalid Variable-Length Datatype Type Tag

## Summary
Severity: Medium
Advisory: CVE-2026-17574
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-17574
Type: osv

## Details
HDF5 contains a NULL pointer dereference vulnerability. Processing a crafted HDF5 file containing an attribute with an invalid variable-length datatype type field may cause the application to crash when the attribute is read.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17574.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17574
- https://github.com/HDFGroup/hdf5/commit/3fa6ed6e9dfeebbc784e21d8c48e31e35a8042bc
