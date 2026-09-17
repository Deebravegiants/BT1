# [H] CVE-2026-42167

## Summary
Severity: High
Advisory: CVE-2026-42167
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-42167
Type: osv

## Details
mod_sql in ProFTPD before 1.3.9a allows remote attackers to execute arbitrary code via a username, in scenarios where there is logging of USER requests with an expansion such as %U, and the SQL backend allows commands (e.g., COPY TO PROGRAM).

## References
- http://www.openwall.com/lists/oss-security/2026/05/01/13
- http://www.openwall.com/lists/oss-security/2026/05/01/4
- http://www.proftpd.org/docs/RELEASE_NOTES-1.3.10rc1
- https://www.openwall.com/lists/oss-security/2026/05/01/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42167.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42167
- https://github.com/proftpd/proftpd/issues/2052
- https://github.com/ZeroPathAI/proftpd-CVE-2026-42167-poc
- https://zeropath.com/blog/proftpd-cve-2026-42167-auth-bypass-privesc-rce
