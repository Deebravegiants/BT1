# [M] Path Traversal in stangirard/quivr

## Summary
Severity: Medium
Advisory: CVE-2024-6583
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-6583
Type: osv

## Details
A path traversal vulnerability exists in the latest version of stangirard/quivr. This vulnerability allows an attacker to upload files to arbitrary paths in an S3 bucket by manipulating the file path in the upload request.

## References
- https://huntr.com/bounties/c310b500-ec26-4121-8d3a-8e863181346f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6583.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6583
