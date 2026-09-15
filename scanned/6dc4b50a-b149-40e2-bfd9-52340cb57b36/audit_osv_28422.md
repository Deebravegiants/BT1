# [H] CVE-2024-32623

## Summary
Severity: High
Advisory: CVE-2024-32623
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32623
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in H5VM_array_fill in H5VM.c (called from H5S_select_elements in H5Spoint.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32623.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32623
