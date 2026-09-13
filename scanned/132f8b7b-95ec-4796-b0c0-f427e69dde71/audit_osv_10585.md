# [M] CVE-2017-17505

## Summary
Severity: Medium
Advisory: CVE-2017-17505
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17505
Type: osv

## Details
In HDF5 1.10.1, there is a NULL pointer dereference in the function H5O_pline_decode in the H5Opline.c file in libhdf5.a. For example, h5dump would crash when someone opens a crafted hdf5 file.

## References
- https://github.com/xiaoqx/pocs/tree/master/hdf5/readme.md
