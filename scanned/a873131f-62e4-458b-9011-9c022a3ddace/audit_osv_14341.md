# [H] CVE-2018-9240

## Summary
Severity: High
Advisory: CVE-2018-9240
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-03
Source: https://osv.dev/vulnerability/CVE-2018-9240
Type: osv

## Details
ncmpc through 0.29 is prone to a NULL pointer dereference flaw. If a user uses the chat screen and another client sends a long chat message, a crash and denial of service could occur.

## References
- https://bugs.debian.org/894724
- https://lists.debian.org/debian-lts-announce/2020/04/msg00020.html
- https://usn.ubuntu.com/4507-1/
