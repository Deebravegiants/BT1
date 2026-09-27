# [C] CVE-2018-18312

## Summary
Severity: Critical
Advisory: CVE-2018-18312
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/CVE-2018-18312
Type: osv

## Details
Perl before 5.26.3 and 5.28.0 before 5.28.1 has a buffer overflow via a crafted regular expression that triggers invalid write operations.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RWQGEB543QN7SSBRKYJM6PSOC3RLYGSM/
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.securityfocus.com/bid/106179
- http://www.securitytracker.com/id/1042181
- https://access.redhat.com/errata/RHSA-2019:0001
- https://access.redhat.com/errata/RHSA-2019:0010
- https://metacpan.org/changes/release/SHAY/perl-5.26.3
- https://metacpan.org/changes/release/SHAY/perl-5.28.1
- https://security.gentoo.org/glsa/201909-01
- https://security.netapp.com/advisory/ntap-20190221-0003/
- https://usn.ubuntu.com/3834-1/
- https://www.debian.org/security/2018/dsa-4347
- https://bugzilla.redhat.com/show_bug.cgi?id=1646734
- https://rt.perl.org/Public/Bug/Display.html?id=133423
