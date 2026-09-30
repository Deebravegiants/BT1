# [M] CVE-2018-17432

## Summary
Severity: Medium
Advisory: CVE-2018-17432
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17432
Type: osv

## Details
A NULL pointer dereference in H5O_sdspace_encode() in H5Osdspace.c in the HDF HDF5 through 1.10.3 library allows attackers to cause a denial of service via a crafted HDF5 file.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln6#null-pointer-dereference-in-h5o_sdspace_encode
