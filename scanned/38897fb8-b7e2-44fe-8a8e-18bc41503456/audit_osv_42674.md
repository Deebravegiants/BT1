# [H] Path traversal in Mattermost Legal Hold plugin via unsanitized file name from federated peer allows arbitrary file write.

## Summary
Severity: High
Advisory: CVE-2026-6957
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-6957
Type: osv

## Details
Mattermost Plugins versions <=1.1.5 fail to sanitize filenames received from federated peers before using them to construct export destination paths, which allows an administrator of a remote federated Mattermost server to write files to arbitrary locations within the target server's filestore via a malicious filename delivered through the shared-channel attachment sync protocol. Mattermost Advisory ID: MMSA-2026-00659

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6957.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-6957
