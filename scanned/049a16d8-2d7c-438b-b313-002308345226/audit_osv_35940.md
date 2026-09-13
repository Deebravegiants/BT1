# [M] Double Free in H5D__chunk_copy() in HDF5 via a Crafted Chunk-Index Size Field

## Summary
Severity: Medium
Advisory: CVE-2026-17573
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-17573
Type: osv

## Details
A double free vulnerability was discovered in the HDF5 library. Processing a crafted HDF5 file containing an oversized chunk size field via h5repack may cause the application to abort due to a double free.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17573.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17573
- https://github.com/HDFGroup/hdf5/issues/6124
