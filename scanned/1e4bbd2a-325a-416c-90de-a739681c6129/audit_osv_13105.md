# [M] CVE-2018-17437

## Summary
Severity: Medium
Advisory: CVE-2018-17437
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17437
Type: osv

## Details
Memory leak in the H5O_dtype_decode_helper() function in H5Odtype.c in the HDF HDF5 through 1.10.3 library allows attackers to cause a denial of service (memory consumption) via a crafted HDF5 file.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00009.html
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln5#memory-leak-in-h5o_dtype_decode_helper
