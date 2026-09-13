# [M] CVE-2018-17433

## Summary
Severity: Medium
Advisory: CVE-2018-17433
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17433
Type: osv

## Details
A heap-based buffer overflow in ReadGifImageDesc() in gifread.c in the HDF HDF5 through 1.10.3 library allows attackers to cause a denial of service via a crafted HDF5 file. This issue was triggered while converting a GIF file to an HDF file.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/HDF5/vuln8#heap-overflow-in-readgifimagedesc
