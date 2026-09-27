# [M] CVE-2019-19344

## Summary
Severity: Medium
Advisory: CVE-2019-19344
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2019-19344
Type: osv

## Details
There is a use-after-free issue in all samba 4.9.x versions before 4.9.18, all samba 4.10.x versions before 4.10.12 and all samba 4.11.x versions before 4.11.5, essentially due to a call to realloc() while other local variables still point at the original buffer.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ACZVNMIFQGGXNJPMHAVBN3H2U65FXQY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GQ6U65I2K23YJC4FESW477WL55TU3PPT/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00055.html
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20200122-0001/
- https://usn.ubuntu.com/4244-1/
- https://www.samba.org/samba/security/CVE-2019-19344.html
- https://www.synology.com/security/advisory/Synology_SA_20_01
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-19344
