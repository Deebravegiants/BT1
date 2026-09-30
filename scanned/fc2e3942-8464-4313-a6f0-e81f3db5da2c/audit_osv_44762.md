# [C] Unidata netcdf-c through 4.10.1 Out-of-bounds Write via Oversized HDF5 Attribute Name

## Summary
Severity: Critical
Advisory: CVE-2026-86095
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-86095
Type: osv

## Details
Unidata netcdf-c through 4.10.1 contains an out-of-bounds write vulnerability in NC4_HDF5_inq_attname() that copies HDF5 attribute names into a fixed 256-byte buffer without length validation. Attackers can craft HDF5 files with oversized attribute names to overflow the destination buffer, causing memory corruption and crashes when applications enumerate attribute names.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86095
- https://www.vulncheck.com/advisories/unidata-netcdf-c-through-4.10.1-out-of-bounds-write-via-oversized-hdf5-attribute-name
- https://github.com/Unidata/netcdf-c
- https://github.com/Unidata/netcdf-c/blob/v4.10.1/libhdf5/hdf5attr.c
