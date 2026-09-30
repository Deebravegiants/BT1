# [M] CVE-2017-17507

## Summary
Severity: Medium
Advisory: CVE-2017-17507
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17507
Type: osv

## Details
In HDF5 1.10.1, there is an out of bounds read vulnerability in the function H5T_conv_struct_opt in H5Tconv.c in libhdf5.a. For example, h5dump would crash when someone opens a crafted hdf5 file.

## References
- https://github.com/xiaoqx/pocs/tree/master/hdf5/readme.md
