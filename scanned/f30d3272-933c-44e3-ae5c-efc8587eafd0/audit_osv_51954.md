# [M] CVE-2021-46244

## Summary
Severity: Medium
Advisory: CVE-2021-46244
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-46244
Type: osv

## Details
A Divide By Zero vulnerability exists in HDF5 v1.13.1-1 vis the function H5T__complete_copy () at /hdf5/src/H5T.c. This vulnerability causes an aritmetic exception, leading to a Denial of Service (DoS).

## References
- https://github.com/HDFGroup/hdf5/issues/1327
