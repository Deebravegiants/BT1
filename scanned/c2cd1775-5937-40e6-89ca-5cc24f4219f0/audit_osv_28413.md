# [H] CVE-2024-32612

## Summary
Severity: High
Advisory: CVE-2024-32612
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32612
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer over-read in H5HL__fl_deserialize in H5HLcache.c, resulting in the corruption of the instruction pointer, a different vulnerability than CVE-2024-32613.

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32612.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32612
