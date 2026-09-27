# [H] CVE-2020-14929

## Summary
Severity: High
Advisory: CVE-2020-14929
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-19
Source: https://osv.dev/vulnerability/CVE-2020-14929
Type: osv

## Details
Alpine before 2.23 silently proceeds to use an insecure connection after a /tls is sent in certain circumstances involving PREAUTH, which is a less secure behavior than the alternative of closing the connection and letting the user decide what they would like to do.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YFXQGKZZMP3VSTLZVO5Z7Z6USYIW37A6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZJLY6JDVGDNAJZ3UQDWYWSDBWOAOXMNX/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00025.html
- http://mailman13.u.washington.edu/pipermail/alpine-info/2020-June/008989.html
