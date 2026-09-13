# [H] CVE-2018-14033

## Summary
Severity: High
Advisory: CVE-2018-14033
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-14033
Type: osv

## Details
An issue was discovered in the HDF HDF5 1.8.20 library. There is a heap-based buffer over-read in the function H5O_layout_decode in H5Olayout.c, related to HDmemcpy.

## References
- https://github.com/TeamSeri0us/pocs/blob/master/hdf5/README2.md
