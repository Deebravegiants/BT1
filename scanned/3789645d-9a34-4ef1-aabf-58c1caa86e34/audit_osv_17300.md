# [M] CVE-2020-14392

## Summary
Severity: Medium
Advisory: CVE-2020-14392
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-14392
Type: osv

## Details
An untrusted pointer dereference flaw was found in Perl-DBI < 1.643. A local attacker who is able to manipulate calls to dbd_db_login6_sv() could cause memory corruption, affecting the service's availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JXLKODJ7B57GITDEZZXNSHPK4VBYXYHR/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00074.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00026.html
- https://metacpan.org/pod/distribution/DBI/Changes#Changes-in-DBI-1.643
- https://usn.ubuntu.com/4503-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1877402
