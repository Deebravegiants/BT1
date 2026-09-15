# [H] CVE-2020-7105

## Summary
Severity: High
Advisory: CVE-2020-7105
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-16
Source: https://osv.dev/vulnerability/CVE-2020-7105
Type: osv

## Details
async.c and dict.c in libhiredis.a in hiredis through 0.14.0 allow a NULL pointer dereference because malloc return values are unchecked.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/76ZDGWBV3YEEQ2YC65ZJEQLKQFVFBZHX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZKOTCIYFEWJJILUGL4JQ3CJAM3TWYZ2A/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00028.html
- https://github.com/redis/hiredis/issues/747
