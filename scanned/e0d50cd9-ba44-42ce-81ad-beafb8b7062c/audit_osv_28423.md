# [H] CVE-2024-32624

## Summary
Severity: High
Advisory: CVE-2024-32624
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32624
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in H5T__ref_mem_setnull in H5Tref.c (called from H5T__conv_ref in H5Tconv.c), resulting in the corruption of the instruction pointer.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32624.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32624
