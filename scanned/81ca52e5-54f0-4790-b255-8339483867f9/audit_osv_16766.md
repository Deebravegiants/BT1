# [H] CVE-2019-9639

## Summary
Severity: High
Advisory: CVE-2019-9639
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-09
Source: https://osv.dev/vulnerability/CVE-2019-9639
Type: osv

## Details
An issue was discovered in the EXIF component in PHP before 7.1.27, 7.2.x before 7.2.16, and 7.3.x before 7.3.3. There is an uninitialized read in exif_process_IFD_in_MAKERNOTE because of mishandling the data_len variable.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00104.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00044.html
- https://access.redhat.com/errata/RHSA-2019:2519
- https://access.redhat.com/errata/RHSA-2019:3299
- https://lists.debian.org/debian-lts-announce/2019/03/msg00043.html
- https://usn.ubuntu.com/3922-1/
- https://usn.ubuntu.com/3922-2/
- https://usn.ubuntu.com/3922-3/
- https://www.debian.org/security/2019/dsa-4403
- https://bugs.php.net/bug.php?id=77659
- https://security.netapp.com/advisory/ntap-20190502-0007/
