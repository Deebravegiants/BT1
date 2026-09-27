# [H] CVE-2017-17509

## Summary
Severity: High
Advisory: CVE-2017-17509
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17509
Type: osv

## Details
In HDF5 1.10.1, there is an out of bounds write vulnerability in the function H5G__ent_decode_vec in H5Gcache.c in libhdf5.a. For example, h5dump would crash or possibly have unspecified other impact someone opens a crafted hdf5 file.

## References
- https://github.com/xiaoqx/pocs/tree/master/hdf5/readme.md
