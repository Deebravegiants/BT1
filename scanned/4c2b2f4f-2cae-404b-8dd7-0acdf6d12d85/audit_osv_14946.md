# [M] CVE-2019-12522

## Summary
Severity: Medium
Advisory: CVE-2019-12522
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2019-12522
Type: osv

## Details
An issue was discovered in Squid through 4.7. When Squid is run as root, it spawns its child processes as a lesser user, by default the user nobody. This is done via the leave_suid call. leave_suid leaves the Saved UID as 0. This makes it trivial for an attacker who has compromised the child process to escalate their privileges back to root.

## References
- https://gitlab.com/jeriko.one/security/-/blob/master/squid/CVEs/CVE-2019-12522.txt
- https://security.netapp.com/advisory/ntap-20210205-0006/
