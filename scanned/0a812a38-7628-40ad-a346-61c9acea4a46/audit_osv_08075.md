# [H] CVE-2016-10196

## Summary
Severity: High
Advisory: CVE-2016-10196
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10196
Type: osv

## Details
Stack-based buffer overflow in the evutil_parse_sockaddr_port function in evutil.c in libevent before 2.1.6-beta allows attackers to cause a denial of service (segmentation fault) via vectors involving a long string in brackets in the ip_as_string argument.

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
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1343453
- https://github.com/libevent/libevent/issues/318
- https://github.com/libevent/libevent/commit/329acc18a0768c21ba22522f01a5c7f46cacc4d5
