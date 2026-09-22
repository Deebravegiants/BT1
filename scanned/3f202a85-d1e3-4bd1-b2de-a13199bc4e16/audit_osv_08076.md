# [H] CVE-2016-10197

## Summary
Severity: High
Advisory: CVE-2016-10197
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10197
Type: osv

## Details
The search_make_new function in evdns.c in libevent before 2.1.6-beta allows attackers to cause a denial of service (out-of-bounds read) via an empty hostname.

## References
- http://www.debian.org/security/2017/dsa-3789
- http://www.openwall.com/lists/oss-security/2017/01/31/17
- http://www.openwall.com/lists/oss-security/2017/02/02/7
- http://www.securityfocus.com/bid/96014
- http://www.securitytracker.com/id/1038320
- https://access.redhat.com/errata/RHSA-2017:1104
- https://access.redhat.com/errata/RHSA-2017:1106
- https://access.redhat.com/errata/RHSA-2017:1201
- https://github.com/libevent/libevent/blob/release-2.1.6-beta/ChangeLog
- https://security.gentoo.org/glsa/201705-01
- https://github.com/libevent/libevent/issues/332
- https://github.com/libevent/libevent/commit/ec65c42052d95d2c23d1d837136d1cf1d9ecef9e
