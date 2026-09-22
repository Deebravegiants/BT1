# [M] CVE-2024-32606

## Summary
Severity: Medium
Advisory: CVE-2024-32606
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32606
Type: osv

## Details
HDF5 Library through 1.14.3 may attempt to dereference uninitialized values in h5tools_str_sprint in tools/lib/h5tools_str.c (called from h5tools_dump_simple_data in tools/lib/h5tools_dump.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32606.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32606
