# [H] CVE-2014-10073

## Summary
Severity: High
Advisory: CVE-2014-10073
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2014-10073
Type: osv

## Details
The create_response function in server/server.c in Psensor before 1.1.4 allows Directory Traversal because it lacks a check for whether a file is under the webserver directory.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00026.html
- https://lists.debian.org/debian-lts-announce/2018/04/msg00026.html
- http://git.wpitchoune.net/gitweb/?p=psensor.git%3Ba=blob%3Bf=NEWS
- http://git.wpitchoune.net/gitweb/?p=psensor.git%3Ba=commit%3Bh=48739caa745f9f8002e87af574f03e5dc6ae3447
- http://git.wpitchoune.net/gitweb/?p=psensor.git%3Ba=commit%3Bh=8b10426dcc0246c1712a99460dd470dcb1cc4d9c
