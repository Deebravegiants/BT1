# [H] CVE-2020-14393

## Summary
Severity: High
Advisory: CVE-2020-14393
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-14393
Type: osv

## Details
A buffer overflow was found in perl-DBI < 1.643 in DBI.xs. A local attacker who is able to supply a string longer than 300 characters could cause an out-of-bounds write, affecting the availability of the service or integrity of data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00074.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JXLKODJ7B57GITDEZZXNSHPK4VBYXYHR/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00067.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00026.html
- https://metacpan.org/pod/distribution/DBI/Changes#Changes-in-DBI-1.643
- https://bugzilla.redhat.com/show_bug.cgi?id=1877409
