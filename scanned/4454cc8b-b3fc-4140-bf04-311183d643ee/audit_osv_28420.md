# [C] CVE-2024-32621

## Summary
Severity: Critical
Advisory: CVE-2024-32621
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32621
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer overflow in H5HG_read in H5HG.c (called from H5VL__native_blob_get in H5VLnative_blob.c), resulting in the corruption of the instruction pointer.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32621.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32621
