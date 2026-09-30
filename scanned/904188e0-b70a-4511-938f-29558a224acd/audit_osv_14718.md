# [C] CVE-2019-11034

## Summary
Severity: Critical
Advisory: CVE-2019-11034
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-04-18
Source: https://osv.dev/vulnerability/CVE-2019-11034
Type: osv

## Details
When processing certain files, PHP EXIF extension in versions 7.1.x below 7.1.28, 7.2.x below 7.2.17 and 7.3.x below 7.3.4 can be caused to read past allocated buffer in exif_process_IFD_TAG function. This may lead to information disclosure or crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00044.html
- https://access.redhat.com/errata/RHSA-2019:2519
- https://access.redhat.com/errata/RHSA-2019:3299
- https://lists.debian.org/debian-lts-announce/2019/05/msg00035.html
- https://seclists.org/bugtraq/2019/Sep/38
- https://security.netapp.com/advisory/ntap-20190502-0001/
- https://support.f5.com/csp/article/K44590877
- https://usn.ubuntu.com/3953-1/
- https://usn.ubuntu.com/3953-2/
- https://www.debian.org/security/2019/dsa-4529
- https://bugs.php.net/bug.php?id=77753
