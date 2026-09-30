# [M] CVE-2018-17438

## Summary
Severity: Medium
Advisory: CVE-2018-17438
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17438
Type: osv

## Details
A SIGFPE signal is raised in the function H5D__select_io() of H5Dselect.c in the HDF HDF5 through 1.10.3 library during an attempted parse of a crafted HDF file, because of incorrect protection against division by zero. It could allow a remote denial of service attack.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln4#divided-by-zero---poc_h5d__select_io_h5dselect
