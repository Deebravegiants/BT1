# [M] CVE-2021-46243

## Summary
Severity: Medium
Advisory: CVE-2021-46243
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-46243
Type: osv

## Details
An untrusted pointer dereference vulnerability exists in HDF5 v1.13.1-1 via the function H5O__dtype_decode_helper () at hdf5/src/H5Odtype.c. This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/HDFGroup/hdf5/issues/1326
