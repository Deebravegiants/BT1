# [C] CVE-2024-32615

## Summary
Severity: Critical
Advisory: CVE-2024-32615
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32615
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in H5Z__nbit_decompress_one_byte in H5Znbit.c, caused by the earlier use of an initialized pointer.

## References
- https://github.com/HDFGroup/cve_hdf5/blob/main/CVE_list.md
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32615.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32615
