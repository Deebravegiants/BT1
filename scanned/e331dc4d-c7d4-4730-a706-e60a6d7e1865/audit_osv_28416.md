# [H] CVE-2024-32617

## Summary
Severity: High
Advisory: CVE-2024-32617
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32617
Type: osv

## Details
HDF5 Library through 1.14.3 contains a heap-based buffer over-read caused by the unsafe use of strdup in H5MM_xstrdup in H5MM.c (called from H5G__ent_to_link in H5Glink.c).

## References
- https://www.hdfgroup.org/2024/05/new-hdf5-cve-issues-fixed-in-1-14-4/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32617.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32617
