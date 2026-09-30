# [C] Zip Path Traversal in Deepin-Compressor

## Summary
Severity: Critical
Advisory: CVE-2023-50255
Aliases: GHSA-rw5r-8p9h-3gp2
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/CVE-2023-50255
Type: osv

## Details
Deepin-Compressor is the default archive manager of Deepin Linux OS. Prior to 5.12.21, there's a path traversal vulnerability in deepin-compressor that can be exploited to achieve Remote Command Execution on the target system upon opening crafted archives. Users are advised to update to version 5.12.21 which addresses the issue. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50255.json
- https://github.com/linuxdeepin/developer-center/security/advisories/GHSA-rw5r-8p9h-3gp2
- https://nvd.nist.gov/vuln/detail/CVE-2023-50255
- https://github.com/linuxdeepin/deepin-compressor/commit/82f668c78c133873f5094cfab6e4eabc0b70e4b6
