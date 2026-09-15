# [M] CVE-2018-17233

## Summary
Severity: Medium
Advisory: CVE-2018-17233
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-20
Source: https://osv.dev/vulnerability/CVE-2018-17233
Type: osv

## Details
A SIGFPE signal is raised in the function H5D__create_chunk_file_map_hyper() of H5Dchunk.c in the HDF HDF5 through 1.10.3 library during an attempted parse of a crafted HDF file, because of incorrect protection against division by zero. It could allow a remote denial of service attack.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00009.html
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln2#divided-by-zero---h5d__create_chunk_file_map_hyper_div_zero
