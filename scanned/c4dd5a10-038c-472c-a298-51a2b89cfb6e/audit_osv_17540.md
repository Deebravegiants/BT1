# [H] CVE-2020-16136

## Summary
Severity: High
Advisory: CVE-2020-16136
Aliases: GHSA-r8pp-42wr-2gc4
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2020-07-31
Source: https://osv.dev/vulnerability/CVE-2020-16136
Type: osv

## Details
In tgstation-server 4.4.0 and 4.4.1, an authenticated user with permission to download logs can download any file on the server machine (accessible by the owner of the server process) via directory traversal ../ sequences in /Administration/Logs/ requests. The attacker is unable to enumerate files, however.

## References
- https://github.com/tgstation/tgstation-server
- https://github.com/tgstation/tgstation-server/security/advisories/GHSA-r8pp-42wr-2gc4
