# [C] CVE-2018-13876

## Summary
Severity: Critical
Advisory: CVE-2018-13876
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-13876
Type: osv

## Details
An issue was discovered in the HDF HDF5 1.8.20 library. There is a stack-based buffer overflow in the function H5FD_sec2_read in H5FDsec2.c, related to HDread.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/hdf5
