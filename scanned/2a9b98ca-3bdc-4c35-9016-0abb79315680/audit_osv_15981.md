# [M] CVE-2019-20919

## Summary
Severity: Medium
Advisory: CVE-2019-20919
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2019-20919
Type: osv

## Details
An issue was discovered in the DBI module before 1.643 for Perl. The hv_fetch() documentation requires checking for NULL and the code does that. But, shortly thereafter, it calls SvOK(profile), causing a NULL pointer dereference.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JXLKODJ7B57GITDEZZXNSHPK4VBYXYHR/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00026.html
- https://metacpan.org/pod/distribution/DBI/Changes#Changes-in-DBI-1.643-...
- https://usn.ubuntu.com/4534-1/
- https://github.com/perl5-dbi/dbi/commit/eca7d7c8f43d96f6277e86d1000e842eb4cc67ff
