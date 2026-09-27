# [H] CVE-2025-63647

## Summary
Severity: High
Advisory: CVE-2025-63647
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-63647
Type: osv

## Details
A NULL pointer dereference in the parse_meta function (src/httpd_daap.c) of owntone-server commit 334beb allows attackers to cause a Denial of Service (DoS) via sending a crafted DAAP request to the server.

## References
- https://github.com/archersec/poc/tree/master/owntone-server
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63647.json
- https://github.com/archersec/security-advisories/blob/master/owntone-server/owntone-server-advisory-2025.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-63647
- https://github.com/owntone/owntone-server/commit/53ee9a3c3921e5448f502800c4dfa787865f6cb7
