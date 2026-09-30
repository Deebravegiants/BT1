# [M] CVE-2018-11203

## Summary
Severity: Medium
Advisory: CVE-2018-11203
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CVE-2018-11203
Type: osv

## Details
A division by zero was discovered in H5D__btree_decode_key in H5Dbtree.c in the HDF HDF5 1.10.2 library. It could allow a remote denial of service attack.

## References
- https://github.com/Twi1ight/fuzzing-pocs/tree/master/hdf5
