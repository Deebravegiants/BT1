# [H] CVE-2025-70084

## Summary
Severity: High
Advisory: CVE-2025-70084
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2025-70084
Type: osv

## Details
Directory traversal vulnerability in OpenSatKit 2.2.1 allows attackers to gain access to sensitive information or delete arbitrary files via crafted value to the FileUtil_GetFileInfo function.

## References
- https://gist.github.com/jonafk555
- https://github.com/OpenSatKit/OpenSatKit/releases/tag/v2.2.1
- https://raw.githubusercontent.com/OpenSatKit/OpenSatKit/master/cfs/apps/filemgr/fsw/src/dir.c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70084.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70084
- https://github.com/OpenSatKit/OpenSatKit
