# [M] CVE-2020-15261

## Summary
Severity: Medium
Advisory: CVE-2020-15261
Aliases: GHSA-c8cc-x786-hqqp
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-19
Source: https://osv.dev/vulnerability/CVE-2020-15261
Type: osv

## Details
On Windows the Veyon Service before version 4.4.2 contains an unquoted service path vulnerability, allowing locally authenticated users with administrative privileges to run malicious executables with LocalSystem privileges. Since Veyon users (both students and teachers) usually don't have administrative privileges, this vulnerability is only dangerous in anyway unsafe setups. The problem has been fixed in version 4.4.2. As a workaround, the exploitation of the vulnerability can be prevented by revoking administrative privileges from all potentially untrustworthy users.

## References
- https://github.com/veyon/veyon/security/advisories/GHSA-c8cc-x786-hqqp
- https://github.com/veyon/veyon/issues/657
- https://github.com/veyon/veyon/commit/f231ec511b9a09f43f49b2c7bb7c60b8046276b1
- http://packetstormsecurity.com/files/162873/Veyon-4.4.1-Unquoted-Service-Path.html
- https://www.exploit-db.com/exploits/48246
- https://www.exploit-db.com/exploits/49925
