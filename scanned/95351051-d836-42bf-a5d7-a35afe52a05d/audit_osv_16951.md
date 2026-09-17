# [M] CVE-2020-10810

## Summary
Severity: Medium
Advisory: CVE-2020-10810
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-22
Source: https://osv.dev/vulnerability/CVE-2020-10810
Type: osv

## Details
An issue was discovered in HDF5 through 1.12.0. A NULL pointer dereference exists in the function H5AC_unpin_entry() located in H5AC.c. It allows an attacker to cause Denial of Service.

## References
- https://bitbucket.hdfgroup.org/projects/HDFFV/repos/hdf5/browse/release_docs/RELEASE.txt
- https://github.com/Loginsoft-Research/hdf5-reports/tree/master/Vuln_3
- https://research.loginsoft.com/bugs/null-pointer-dereference-in-h5ac-c-hdf5-1-13-0/
