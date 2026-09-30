# [H] CVE-2025-50735

## Summary
Severity: High
Advisory: CVE-2025-50735
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-03
Source: https://osv.dev/vulnerability/CVE-2025-50735
Type: osv

## Details
Directory traversal vulnerability in NextChat thru 2.16.0 due to the WebDAV proxy failing to canonicalize or reject dot path segments in its catch-all route, allowing attackers to gain sensitive information via authenticated or anonymous WebDAV endpoints.

## References
- https://github.com/ChatGPTNextWeb/NextChat/blob/main/app/api/webdav/%5B...path%5D/route.ts
- https://github.com/ChatGPTNextWeb/NextChat/blob/main/app/utils/cloud/webdav.ts
- https://github.com/fai1424/Vulnerability-Research/tree/main/CVE-2025-50735
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50735.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50735
