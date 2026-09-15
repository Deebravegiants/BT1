# [M] Buffer underflow in `H5Iget_name `/`H5G_get_name` if size is zero

## Summary
Severity: Medium
Advisory: CVE-2026-26199
Aliases: GHSA-5c6x-jmgf-f5vc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-26199
Type: osv

## Details
HDF5 is a high-performance library and a file format specification that implements the HDF5 data model. If `H5Iget_name` is invoked on a group id with `0` for the size parameter, it will underflow when trying to place a null terminator in the buffer. This can occur if `H5Iget_name` is invoked in a way where `size` can be forced to zero, and there is important data before the `name` buffer.

## References
- https://github.com/HDFGroup/hdf5/blob/develop/src/H5Gname.c#L474
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26199.json
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-5c6x-jmgf-f5vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-26199
