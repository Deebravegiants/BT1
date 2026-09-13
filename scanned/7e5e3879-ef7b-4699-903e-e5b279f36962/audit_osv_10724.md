# [H] CVE-2017-20002

## Summary
Severity: High
Advisory: CVE-2017-20002
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-17
Source: https://osv.dev/vulnerability/CVE-2017-20002
Type: osv

## Details
The Debian shadow package before 1:4.5-1 for Shadow incorrectly lists pts/0 and pts/1 as physical terminals in /etc/securetty. This allows local users to login as password-less users even if they are connected by non-physical means such as SSH (hence bypassing PAM's nullok_secure configuration). This notably affects environments such as virtual machines automatically generated with a default blank root password, allowing all local users to escalate privileges.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=877374
- https://lists.debian.org/debian-lts-announce/2021/03/msg00020.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=914957
