# [H] CVE-2025-57156

## Summary
Severity: High
Advisory: CVE-2025-57156
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-57156
Type: osv

## Details
NULL pointer dereference in the dacp_reply_playqueueedit_clear function in src/httpd_dacp.c in owntone-server through commit 6d604a1 (newer commit after version 28.12) allows remote attackers to cause a Denial of Service (crash).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57156.json
- https://github.com/archersec/security-advisories/blob/master/owntone-server/owntone-server-advisory-2025.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-57156
- https://github.com/owntone/owntone-server/issues/1907
- https://github.com/owntone/owntone-server/commit/5e4d40ee03ae22ab79534bb1410fa9db96c9fabd
