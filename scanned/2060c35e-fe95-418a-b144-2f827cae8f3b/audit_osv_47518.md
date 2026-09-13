# [H] CVE-2016-7449

## Summary
Severity: High
Advisory: CVE-2016-7449
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-7449
Type: osv

## Details
The TIFFGetField function in coders/tiff.c in GraphicsMagick 1.3.24 allows remote attackers to cause a denial of service (out-of-bounds heap read) via a file containing an "unterminated" string.

## References
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00094.html
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00097.html
- http://www.openwall.com/lists/oss-security/2016/09/18/8
- http://www.securityfocus.com/bid/93074
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1374233
