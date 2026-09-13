# [H] CVE-2025-57155

## Summary
Severity: High
Advisory: CVE-2025-57155
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-57155
Type: osv

## Details
NULL pointer dereference in the daap_reply_groups function in src/httpd_daap.c in owntone-server through commit 5e6f19a (newer commit after version 28.2) allows remote attackers to cause a Denial of Service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57155.json
- https://github.com/archersec/security-advisories/blob/master/owntone-server/owntone-server-advisory-2025.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-57155
- https://github.com/owntone/owntone-server/commit/d857116e4143a500d6a1ea13f4baa057ba3b0028
