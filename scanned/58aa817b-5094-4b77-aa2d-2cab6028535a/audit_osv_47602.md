# [M] CVE-2016-9082

## Summary
Severity: Medium
Advisory: CVE-2016-9082
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-9082
Type: osv

## Details
Integer overflow in the write_png function in cairo 1.14.6 allows remote attackers to cause a denial of service (invalid pointer dereference) via a large svg file.

## References
- https://security.gentoo.org/glsa/201904-01
- http://www.openwall.com/lists/oss-security/2016/10/27/2
- http://www.securityfocus.com/bid/93931
- https://bugzilla.redhat.com/show_bug.cgi?id=1312337
- https://bugs.freedesktop.org/attachment.cgi?id=127421
- https://bugs.freedesktop.org/show_bug.cgi?id=98165
