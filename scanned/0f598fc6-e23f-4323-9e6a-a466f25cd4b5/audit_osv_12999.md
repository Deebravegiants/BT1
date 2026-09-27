# [C] CVE-2018-16842

## Summary
Severity: Critical
Advisory: CVE-2018-16842
Aliases: CURL-CVE-2018-16842
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-16842
Type: osv

## Details
Curl versions 7.14.1 through 7.61.1 are vulnerable to a heap-based buffer over-read in the tool_msgs.c:voutf() function that may result in information exposure and denial of service.

## References
- http://www.securitytracker.com/id/1042014
- https://access.redhat.com/errata/RHSA-2019:2181
- https://lists.debian.org/debian-lts-announce/2018/11/msg00005.html
- https://security.gentoo.org/glsa/201903-03
- https://usn.ubuntu.com/3805-1/
- https://usn.ubuntu.com/3805-2/
- https://www.debian.org/security/2018/dsa-4331
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16842
- https://curl.haxx.se/docs/CVE-2018-16842.html
- https://github.com/curl/curl/commit/d530e92f59ae9bb2d47066c3c460b25d2ffeb211
