# [H] CVE-2018-14647

## Summary
Severity: High
Advisory: CVE-2018-14647
Aliases: PSF-2018-5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-25
Source: https://osv.dev/vulnerability/CVE-2018-14647
Type: osv

## Details
Python's elementtree C accelerator failed to initialise Expat's hash salt during initialization. This could make it easy to conduct denial of service attacks against Expat by constructing an XML document that would cause pathological hash collisions in Expat's internal data structures, consuming large amounts CPU and RAM. The vulnerability exists in Python versions 3.7.0, 3.6.0 through 3.6.6, 3.5.0 through 3.5.6, 3.4.0 through 3.4.9, 2.7.0 through 2.7.15.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RBJCB2HWOJLP3L7CUQHJHNBHLSVOXJE5/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- http://www.securityfocus.com/bid/105396
- http://www.securitytracker.com/id/1041740
- https://access.redhat.com/errata/RHSA-2019:1260
- https://access.redhat.com/errata/RHSA-2019:2030
- https://access.redhat.com/errata/RHSA-2019:3725
- https://lists.debian.org/debian-lts-announce/2019/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00023.html
- https://usn.ubuntu.com/3817-1/
- https://usn.ubuntu.com/3817-2/
- https://www.debian.org/security/2018/dsa-4306
- https://www.debian.org/security/2018/dsa-4307
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14647
- https://bugs.python.org/issue34623
