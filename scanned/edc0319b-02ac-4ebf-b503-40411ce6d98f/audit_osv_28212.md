# [H] CVE-2024-29165

## Summary
Severity: High
Advisory: CVE-2024-29165
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-29165
Type: osv

## Details
HDF5 through 1.14.3 contains a buffer overflow in H5Z__filter_fletcher32, resulting in the corruption of the instruction pointer and causing denial of service or potential code execution.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29165.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29165
