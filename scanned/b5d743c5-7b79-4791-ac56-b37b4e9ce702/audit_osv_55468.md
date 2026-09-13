# [M] GHSL-2025-059 - 7-Zip - Null pointer array write attempt in NArchive::NCom::CHandler::GetStream

## Summary
Severity: Medium
Advisory: CVE-2025-53817
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-53817
Type: osv

## Details
7-Zip is a file archiver with a high compression ratio. 7-Zip supports extracting from Compound Documents. Prior to version 25.0.0, a null pointer dereference in the Compound handler may lead to denial of service. Version 25.0.0 contains a fix cor the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/18/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53817.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53817
- https://securitylab.github.com/advisories/GHSL-2025-059_7-Zip/
- https://www.openwall.com/lists/oss-security/2025/07/18/2
