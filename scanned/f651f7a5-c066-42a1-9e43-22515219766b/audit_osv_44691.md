# [M] SiYuan before v3.8.2 Path Guard Bypass via Case Mismatch

## Summary
Severity: Medium
Advisory: CVE-2026-85580
Aliases: GHSA-mmgw-3mx9-cfwp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85580
Type: osv

## Details
SiYuan versions before v3.8.2 contain a path guard bypass vulnerability in the MCP file-access handler that uses case-sensitive matching on Linux filesystems. Attackers can read the protected publishAccess.json file by requesting case-variant paths like PublishAccess.json to disclose sensitive publish-access configuration and metadata.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85580.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-mmgw-3mx9-cfwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-85580
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-path-guard-bypass-via-case-mismatch
