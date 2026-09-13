# [M] SiYuan before v3.8.1 Missing Authorization via /history and /repo/diff

## Summary
Severity: Medium
Advisory: CVE-2026-82651
Aliases: GHSA-3cm4-ccvw-6xr6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82651
Type: osv

## Details
SiYuan before v3.8.1 does not apply the IsForbiddenAbsPath guard (introduced in GHSA-c8r8-95hg-mp34) to the /history/*path and /repo/diff/*path endpoints in kernel/server/serve.go. These routes require admin authentication but construct file paths independently, so an authenticated administrator can retrieve historical snapshots of sensitive files that the guard is meant to block, including data/.siyuan/publishAccess.json (plaintext publish-mode passwords) and files under data/templates/.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82651.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-3cm4-ccvw-6xr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-82651
- https://www.vulncheck.com/advisories/siyuan-before-3.8.1-missing-authorization-via-history-and-repo-diff
