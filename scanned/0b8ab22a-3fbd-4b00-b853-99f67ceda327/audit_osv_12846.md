# [M] CVE-2018-15671

## Summary
Severity: Medium
Advisory: CVE-2018-15671
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-15671
Type: osv

## Details
An issue was discovered in the HDF HDF5 1.10.2 library. Excessive stack consumption has been detected in the function H5P__get_cb() in H5Pint.c during an attempted parse of a crafted HDF file. This results in denial of service.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5#stack-overflow---stackoverflow_h5p__get_cb
