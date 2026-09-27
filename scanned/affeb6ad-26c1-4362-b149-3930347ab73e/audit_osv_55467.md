# [M] GHSL-2025-058 - 7-Zip Multi-byte write heap buffer overflow in NCompress::NRar5::CDecoder

## Summary
Severity: Medium
Advisory: CVE-2025-53816
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-53816
Type: osv

## Details
7-Zip is a file archiver with a high compression ratio. Zeroes written outside heap buffer in RAR5 handler may lead to memory corruption and denial of service in versions of 7-Zip prior to 25.0.0. Version 25.0.0 contains a fix for the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/18/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53816.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53816
- https://securitylab.github.com/advisories/GHSL-2025-058_7-Zip/
- https://www.openwall.com/lists/oss-security/2025/07/18/1
