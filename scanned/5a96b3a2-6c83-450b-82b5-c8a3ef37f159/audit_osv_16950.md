# [M] CVE-2020-10809

## Summary
Severity: Medium
Advisory: CVE-2020-10809
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-22
Source: https://osv.dev/vulnerability/CVE-2020-10809
Type: osv

## Details
An issue was discovered in HDF5 through 1.12.0. A heap-based buffer overflow exists in the function Decompress() located in decompress.c. It can be triggered by sending a crafted file to the gif2h5 binary. It allows an attacker to cause Denial of Service.

## References
- https://bitbucket.hdfgroup.org/projects/HDFFV/repos/hdf5/browse/release_docs/RELEASE.txt
- https://github.com/Loginsoft-Research/hdf5-reports/tree/master/Vuln_1
- https://research.loginsoft.com/bugs/heap-overflow-in-decompress-c-hdf5-1-13-0/
