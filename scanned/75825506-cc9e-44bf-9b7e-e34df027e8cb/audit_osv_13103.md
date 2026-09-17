# [M] CVE-2018-17435

## Summary
Severity: Medium
Advisory: CVE-2018-17435
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17435
Type: osv

## Details
A heap-based buffer over-read in H5O_attr_decode() in H5Oattr.c in the HDF HDF5 through 1.10.3 library allows attackers to cause a denial of service via a crafted HDF5 file. This issue was triggered while converting an HDF file to GIF file.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln7#heap-overflow-in-h5o_attr_decode
