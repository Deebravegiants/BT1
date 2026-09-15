# [C] CVE-2024-32608

## Summary
Severity: Critical
Advisory: CVE-2024-32608
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-32608
Type: osv

## Details
HDF5 library through 1.14.3 has memory corruption in H5A__close resulting in the corruption of the instruction pointer and causing denial of service or potential code execution.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32608.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32608
