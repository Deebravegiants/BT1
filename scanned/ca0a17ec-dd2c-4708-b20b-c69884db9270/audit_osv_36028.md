# [M] HDF5 h5dump Untrusted Pointer Dereference in Binary Output of Variable-Length String Datasets

## Summary
Severity: Medium
Advisory: CVE-2026-19023
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-19023
Type: osv

## Details
Untrusted pointer dereference in the render_bin_output function in the h5dump tool in HDF5 before 2.3.0 allows attackers to cause a denial of service via a variable-length string dataset with more than one element dumped in binary mode, which corrupts the per-element stride calculation and causes subsequent elements to be read from a misaligned offset and dereferenced as a pointer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19023.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19023
- https://github.com/HDFGroup/hdf5/issues/6486
