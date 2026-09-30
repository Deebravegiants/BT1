# [C] CVE-2018-20721

## Summary
Severity: Critical
Advisory: CVE-2018-20721
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2018-20721
Type: osv

## Details
URI_FUNC() in UriParse.c in uriparser before 0.9.1 has an out-of-bounds read (in uriParse*Ex* functions) for an incomplete URI with an IPv6 address containing an embedded IPv4 address, such as a "//[::44.1" address.

## References
- https://github.com/uriparser/uriparser/blob/master/ChangeLog
- https://lists.debian.org/debian-lts-announce/2019/02/msg00028.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00029.html
- https://github.com/uriparser/uriparser/commit/cef25028de5ff872c2e1f0a6c562eb3ea9ecbce4
