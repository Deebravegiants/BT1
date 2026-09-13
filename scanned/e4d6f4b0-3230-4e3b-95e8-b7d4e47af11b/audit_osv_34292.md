# [M] CVE-2025-57682

## Summary
Severity: Medium
Advisory: CVE-2025-57682
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-57682
Type: osv

## Details
Directory Traversal vulnerability in Papermark 0.20.0 and prior allows authenticated attackers to retrieve arbitrary files from an S3 bucket through its CloudFront distribution via the "POST /api/file/s3/get-presigned-get-url-proxy" API

## References
- https://github.com/dos-m0nk3y/CVE/tree/main/CVE-2025-57682
- https://papermark.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57682.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57682
- https://github.com/mfts/papermark
