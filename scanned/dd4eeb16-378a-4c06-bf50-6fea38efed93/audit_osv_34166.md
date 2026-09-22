# [M] qBit Manage Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-55295
Aliases: GHSA-vh56-26wq-vvfv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-55295
Type: osv

## Details
qBit Manage is a tool that helps manage tedious tasks in qBittorrent and automate them. A path traversal vulnerability exists in qbit_manage's web API that allows authenticated users to read arbitrary files from the server filesystem through the restore_config_from_backup endpoint. The vulnerability allows attackers to bypass directory restrictions and read arbitrary files from the server filesystem by manipulating the backup_id parameter with path traversal sequences (e.g., ../). This vulnerability is fixed in 4.5.4.

## References
- https://github.com/StuffAnThings/qbit_manage/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55295.json
- https://github.com/StuffAnThings/qbit_manage/security/advisories/GHSA-vh56-26wq-vvfv
- https://nvd.nist.gov/vuln/detail/CVE-2025-55295
