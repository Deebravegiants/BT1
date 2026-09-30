# [M] CVE-2024-32607

## Summary
Severity: Medium
Advisory: CVE-2024-32607
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32607
Type: osv

## Details
HDF5 Library through 1.14.3 has a SEGV in H5A__close in H5Aint.c, resulting in the corruption of the instruction pointer.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32607.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32607
