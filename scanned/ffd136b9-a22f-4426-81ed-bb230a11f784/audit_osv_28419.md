# [H] CVE-2024-32620

## Summary
Severity: High
Advisory: CVE-2024-32620
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32620
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer over-read in H5F_addr_decode_len in H5Fint.c, resulting in the corruption of the instruction pointer.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32620.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32620
