# [H] CVE-2025-63648

## Summary
Severity: High
Advisory: CVE-2025-63648
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-63648
Type: osv

## Details
A NULL pointer dereference in the dacp_reply_playqueueedit_move function (src/httpd_dacp.c) of owntone-server commit b7e385f allows attackers to cause a Denial of Service (DoS) via sending a crafted DACP request to the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63648.json
- https://github.com/archersec/security-advisories/blob/master/owntone-server/owntone-server-advisory-2025.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-63648
- https://github.com/owntone/owntone-server/issues/1933
- https://github.com/owntone/owntone-server/commit/5f526c7a7e08c567a5c72421d74a79dafdd07621
