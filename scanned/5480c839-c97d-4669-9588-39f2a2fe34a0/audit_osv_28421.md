# [C] CVE-2024-32622

## Summary
Severity: Critical
Advisory: CVE-2024-32622
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32622
Type: osv

## Details
HDF5 Library through 1.14.3 contains a out-of-bounds read operation in H5FL_arr_malloc in H5FL.c (called from H5S_set_extent_simple in H5S.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32622.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32622
