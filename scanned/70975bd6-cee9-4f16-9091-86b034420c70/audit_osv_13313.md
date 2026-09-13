# [C] CVE-2018-19198

## Summary
Severity: Critical
Advisory: CVE-2018-19198
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19198
Type: osv

## Details
An issue was discovered in uriparser before 0.9.0. UriQuery.c allows an out-of-bounds write via a uriComposeQuery* or uriComposeQueryEx* function because the '&' character is mishandled in certain contexts.

## References
- https://access.redhat.com/errata/RHSA-2019:2280
- https://github.com/uriparser/uriparser/blob/uriparser-0.9.0/ChangeLog
- https://lists.debian.org/debian-lts-announce/2018/11/msg00019.html
- https://github.com/uriparser/uriparser/commit/864f5d4c127def386dd5cc926ad96934b297f04e
