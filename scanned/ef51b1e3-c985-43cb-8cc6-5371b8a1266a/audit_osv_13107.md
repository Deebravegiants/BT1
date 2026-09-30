# [M] CVE-2018-17439

## Summary
Severity: Medium
Advisory: CVE-2018-17439
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17439
Type: osv

## Details
An issue was discovered in the HDF HDF5 1.10.3 library. There is a stack-based buffer overflow in the function H5S_extent_get_dims() in H5S.c. Specifically, this issue occurs while converting an HDF5 file to a GIF file.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln5#stack-overflow-in-h5s_extent_get_dims
