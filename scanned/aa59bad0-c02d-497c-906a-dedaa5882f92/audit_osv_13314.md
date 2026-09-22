# [C] CVE-2018-19199

## Summary
Severity: Critical
Advisory: CVE-2018-19199
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19199
Type: osv

## Details
An issue was discovered in uriparser before 0.9.0. UriQuery.c allows an integer overflow via a uriComposeQuery* or uriComposeQueryEx* function because of an unchecked multiplication.

## References
- https://access.redhat.com/errata/RHSA-2019:2280
- https://lists.debian.org/debian-lts-announce/2018/11/msg00019.html
- https://github.com/uriparser/uriparser/blob/uriparser-0.9.0/ChangeLog
- https://github.com/uriparser/uriparser/commit/f76275d4a91b28d687250525d3a0c5509bbd666f
