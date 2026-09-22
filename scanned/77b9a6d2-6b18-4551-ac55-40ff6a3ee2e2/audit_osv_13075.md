# [M] CVE-2018-17237

## Summary
Severity: Medium
Advisory: CVE-2018-17237
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-20
Source: https://osv.dev/vulnerability/CVE-2018-17237
Type: osv

## Details
A SIGFPE signal is raised in the function H5D__chunk_set_info_real() of H5Dchunk.c in the HDF HDF5 1.10.3 library during an attempted parse of a crafted HDF file, because of incorrect protection against division by zero. This issue is different from CVE-2018-11207.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00009.html
- https://github.com/SegfaultMasters/covering360/blob/master/HDF5/README.md#divided-by-zero---h5d__chunk_set_info_real_div_by_zero
