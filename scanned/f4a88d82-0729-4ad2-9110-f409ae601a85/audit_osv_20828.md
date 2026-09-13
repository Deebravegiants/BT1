# [H] CVE-2021-37501

## Summary
Severity: High
Advisory: CVE-2021-37501
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/CVE-2021-37501
Type: osv

## Details
Buffer Overflow vulnerability in HDFGroup hdf5-h5dump 1.12.0 through 1.13.0 allows attackers to cause a denial of service via h5tools_str_sprint in /hdf5/tools/lib/h5tools_str.c.

## References
- https://github.com/HDFGroup/hdf5/issues/2458
- https://github.com/HDFGroup/hdf5
- https://github.com/ST4RF4LL/Something_Found/blob/main/HDF5_v1.13.0_h5dump_heap_overflow.md
