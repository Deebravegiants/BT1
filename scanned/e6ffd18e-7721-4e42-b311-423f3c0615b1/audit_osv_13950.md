# [H] CVE-2018-5740

## Summary
Severity: High
Advisory: CVE-2018-5740
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5740
Type: osv

## Details
"deny-answer-aliases" is a little-used feature intended to help recursive server operators protect end users against DNS rebinding attacks, a potential method of circumventing the security model used by client browsers. However, a defect in this feature makes it easy, when the feature is in use, to experience an assertion failure in name.c. Affects BIND 9.7.0->9.8.8, 9.9.0->9.9.13, 9.10.0->9.10.8, 9.11.0->9.11.4, 9.12.0->9.12.2, 9.13.0->9.13.2.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00027.html
- http://www.securityfocus.com/bid/105055
- http://www.securitytracker.com/id/1041436
- https://access.redhat.com/errata/RHSA-2018:2570
- https://access.redhat.com/errata/RHSA-2018:2571
- https://kb.isc.org/docs/aa-01639
- https://lists.debian.org/debian-lts-announce/2018/08/msg00033.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00001.html
- https://security.gentoo.org/glsa/201903-13
- https://security.netapp.com/advisory/ntap-20180926-0003/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03927en_us
- https://usn.ubuntu.com/3769-1/
- https://usn.ubuntu.com/3769-2/
