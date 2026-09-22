# [H] CVE-2018-19200

## Summary
Severity: High
Advisory: CVE-2018-19200
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19200
Type: osv

## Details
An issue was discovered in uriparser before 0.9.0. UriCommon.c allows attempted operations on NULL input via a uriResetUri* function.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00019.html
- https://github.com/uriparser/uriparser/blob/uriparser-0.9.0/ChangeLog
- https://github.com/uriparser/uriparser/commit/f58c25069cf4a986fe17a80c5b38687e31feb539
