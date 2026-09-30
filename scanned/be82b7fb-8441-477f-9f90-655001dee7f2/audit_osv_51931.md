# [M] CVE-2021-45830

## Summary
Severity: Medium
Advisory: CVE-2021-45830
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-05
Source: https://osv.dev/vulnerability/CVE-2021-45830
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in HDF5 1.13.1-1 via H5F_addr_decode_len in /hdf5/src/H5Fint.c, which could cause a Denial of Service.

## References
- https://github.com/HDFGroup/hdf5/issues/1314
