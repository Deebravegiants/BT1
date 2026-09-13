# [C] CVE-2024-42458

## Summary
Severity: Critical
Advisory: CVE-2024-42458
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-02
Source: https://osv.dev/vulnerability/CVE-2024-42458
Type: osv

## Details
server.c in Neat VNC (aka neatvnc) before 0.8.1 does not properly validate the security type, a related issue to CVE-2006-2369.

## References
- https://github.com/any1/neatvnc/compare/v0.8.0...v0.8.1
- https://github.com/any1/neatvnc/releases/tag/v0.8.1
- https://www.openwall.com/lists/oss-security/2024/08/02/1
- https://www.openwall.com/lists/oss-security/2024/08/02/10
- https://www.openwall.com/lists/oss-security/2024/08/02/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42458.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42458
- https://github.com/any1/neatvnc/commit/cc71650a69abc2573a0d96d082409d2468802d47
