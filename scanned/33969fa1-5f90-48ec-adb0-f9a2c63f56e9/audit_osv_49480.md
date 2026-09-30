# [C] CVE-2019-13273

## Summary
Severity: Critical
Advisory: CVE-2019-13273
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-27
Source: https://osv.dev/vulnerability/CVE-2019-13273
Type: osv

## Details
In Xymon through 4.3.28, a buffer overflow vulnerability exists in the csvinfo CGI script. The overflow may be exploited by sending a crafted GET request that triggers an sprintf of the srcdb parameter.

## References
- https://github.com/svn2github/xymon/blob/master/branches/4.3.28/web/csvinfo.c
- https://lists.debian.org/debian-lts-announce/2019/08/msg00032.html
