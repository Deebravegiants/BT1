# [H] CVE-2024-29161

## Summary
Severity: High
Advisory: CVE-2024-29161
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-29161
Type: osv

## Details
HDF5 through 1.14.3 contains a heap buffer overflow in H5A__attr_release_table, resulting in the corruption of the instruction pointer and causing denial of service or potential code execution.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29161.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29161
