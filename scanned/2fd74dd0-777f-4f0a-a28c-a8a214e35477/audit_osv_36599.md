# [M] Open eClass Has File Upload Filter Bypass via ZIP Archive Extraction

## Summary
Severity: Medium
Advisory: CVE-2026-24673
Aliases: GHSA-3g4j-56gp-v6wv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24673
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, a file upload validation bypass vulnerability allows attackers to upload files with prohibited extensions by embedding them inside ZIP archives and extracting them using the application’s built-in decompression functionality. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24673.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-3g4j-56gp-v6wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-24673
