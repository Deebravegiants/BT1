# [M] CVE-2026-26824

## Summary
Severity: Medium
Advisory: CVE-2026-26824
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-26824
Type: osv

## Details
libxls through version 1.6.3 contains a use of uninitialized memory vulnerability in the OLE container parser. Memory allocated for the Master Sector Allocation Table (MSAT) in read_MSAT() is not fully initialized before being consumed by ole2_validate_sector_chain(), which may result in application crashes or potential information disclosure when processing a crafted XLS file

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26824.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26824
- https://github.com/libxls/libxls/issues/155
