# [C] xShop: Unrestricted File Upload in File Attachment Module in Admin panel leads to Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-49849
Aliases: GHSA-fc35-qjg3-f6g7
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-49849
Type: osv

## Details
xShop is an open-source shop developed in Laravel. An Unrestricted File Upload vulnerability in xShop version 3.0.3 allows an authenticated administrator to upload executable files (e.g., .php). By uploading a specially crafted php file, an attacker can achieve Remote Code Execution (RCE) on the server, leading to a full system compromise. Version 3.0.4 fixes the issue.

## References
- https://github.com/4xmen/xshop/releases/tag/v3.0.4
- https://github.com/4xmen/xshop/security/advisories/GHSA-fc35-qjg3-f6g7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49849.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49849
- https://github.com/4xmen/xshop/commit/dd4a3add9d6f5b5f9dde9685e97f51057903a1db
- https://github.com/4xmen/xshop/pull/64
